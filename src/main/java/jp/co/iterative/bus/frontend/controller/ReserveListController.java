package jp.co.iterative.bus.frontend.controller;

import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import jp.co.iterative.bus.entity.MemberReservationCustomized;
import jp.co.iterative.bus.entity.SeatReservationExample;
import jp.co.iterative.bus.frontend.form.ReserveDeleteForm;
import jp.co.iterative.bus.frontend.security.MemberDetails;
import jp.co.iterative.bus.mapper.MemberCustomMapper;
import jp.co.iterative.bus.mapper.ReservationMapper;
import jp.co.iterative.bus.mapper.SeatReservationMapper;

@Controller
@RequestMapping("reserveList")
public class ReserveListController {

	// 【削除】private static final int MEMBER_ID = 1;

	@Autowired
	private MemberCustomMapper memberCustomMapper;

	@Autowired
	private ReservationMapper reservationMapper;

	@Autowired
	private SeatReservationMapper seatReservationMapper;

	// 【追加】ログイン中の会員IDを取得
	private Integer getLoginMemberId() {
		MemberDetails memberDetails = (MemberDetails) SecurityContextHolder
				.getContext()
				.getAuthentication()
				.getPrincipal();
		return memberDetails.getMember().getId();
	}

	// 1. 予約一覧
	// 【変更】@RequestMapping("list") → @RequestMapping("display")
	@RequestMapping("display")
	public String list(Model model) {
		// 【変更】MEMBER_ID → getLoginMemberId()
		List<MemberReservationCustomized> allReservations = memberCustomMapper.selectReservationByMemberId(getLoginMemberId());
		// 【追加】日付フィルタリング処理
		LocalDate today = LocalDate.now();

		List<MemberReservationCustomized> filteredReservations = allReservations.stream()
			.filter(r -> r.getRideDate() != null && !toLocalDate(r.getRideDate()).isBefore(today))
			.collect(Collectors.toList());

		model.addAttribute("reservationList", filteredReservations);

		return "reserveList/reserveListDisplay";
	}

	// 2. 削除確認（Formを使用）
	@RequestMapping("deleteConfirm")
	public String deleteConfirm(ReserveDeleteForm reserveDeleteForm, Model model, RedirectAttributes redirectAttributes) {

		// フォームにIDが入っているかチェック
		if (reserveDeleteForm.getReservationId() == null) {
			redirectAttributes.addFlashAttribute("errorMessage", "削除する予約を選択してください。");
			// 【変更】/reserveList/list → /reserveList/display
			return "redirect:/reserveList/display";
		}

		// 【変更】MEMBER_ID → getLoginMemberId()
		List<MemberReservationCustomized> allReservations = memberCustomMapper.selectReservationByMemberId(getLoginMemberId());
		// 【追加】日付フィルタリング処理
		LocalDate today = LocalDate.now();

		List<MemberReservationCustomized> filteredReservations = allReservations.stream()
			.filter(r -> r.getRideDate() != null && !toLocalDate(r.getRideDate()).isBefore(today))
			.collect(Collectors.toList());

		MemberReservationCustomized selectedReservation = filteredReservations.stream()
				.filter(r -> reserveDeleteForm.getReservationId().equals(r.getReservationId()))
				.findFirst()
				.orElse(null);

		if (selectedReservation == null) {
			redirectAttributes.addFlashAttribute("errorMessage", "指定された予約が見つかりません。");
			// 【変更】/reserveList/list → /reserveList/display
			return "redirect:/reserveList/display";
		}

		// 小計の計算
		int totalAmount = 0;
		if (selectedReservation.getPrice() != null && selectedReservation.getSeatNames() != null) {
			totalAmount = selectedReservation.getPrice() * selectedReservation.getSeatNames().size();
		}

		// JSPに渡すデータ（Form自体も画面に渡す）
		model.addAttribute("reservation", selectedReservation);
		model.addAttribute("totalAmount", totalAmount);
		model.addAttribute("reserveDeleteForm", reserveDeleteForm);


		return "reserveList/deleteComfirm";
	}

	// 3. 削除実行（Formを使用）
	@Transactional
	@RequestMapping("delete")
	public String delete(ReserveDeleteForm reserveDeleteForm, RedirectAttributes redirectAttributes) {

		if (reserveDeleteForm.getReservationId() != null) {
			Integer reservationId = reserveDeleteForm.getReservationId();

			// 既に削除されているか確認
			if (reservationMapper.selectByPrimaryKey(reservationId) == null) {
			    redirectAttributes.addFlashAttribute("errorMessage", "指定した予約は既に削除されています。");
			    // 【変更】/reserveList/list → /reserveList/display
			    return "redirect:/reserveList/display";
			}

			// 完了画面表示用にデータを退避
			// 【変更】MEMBER_ID → getLoginMemberId()
			List<MemberReservationCustomized> allReservations = memberCustomMapper.selectReservationByMemberId(getLoginMemberId());
			// 【追加】日付フィルタリング処理
			LocalDate today = LocalDate.now();

			List<MemberReservationCustomized> filteredReservations = allReservations.stream()
				.filter(r -> r.getRideDate() != null && !toLocalDate(r.getRideDate()).isBefore(today))
				.collect(Collectors.toList());

			MemberReservationCustomized canceledReservation = filteredReservations.stream()
					.filter(r -> r.getReservationId().equals(reservationId))
					.findFirst()
					.orElse(null);

			// 【追加】セキュリティチェック：過去の予約は削除不可
			if (canceledReservation == null) {
				redirectAttributes.addFlashAttribute("errorMessage", "指定された予約は削除できません。");
				return "redirect:/reserveList/display";
			}

			redirectAttributes.addFlashAttribute("canceledReservation", canceledReservation);
			if (canceledReservation.getPrice() != null && canceledReservation.getSeatNames() != null) {
				int totalAmount = canceledReservation.getPrice() * canceledReservation.getSeatNames().size();
				redirectAttributes.addFlashAttribute("totalAmount", totalAmount);
			}

			// 削除処理
			SeatReservationExample example = new SeatReservationExample();
			example.createCriteria().andReservationIdEqualTo(reservationId);
			seatReservationMapper.deleteByExample(example);
			reservationMapper.deleteByPrimaryKey(reservationId);
		}


		return "redirect:/reserveList/deleteComplete";
	}

	// 4. 削除完了
	@RequestMapping("deleteComplete")
	public String deleteComplete() {

		return "reserveList/deleteComplete";
	}

	// 【追加】日付変換ユーティリティ
	private LocalDate toLocalDate(Date date) {
		return date.toInstant()
			.atZone(ZoneId.systemDefault())
			.toLocalDate();
	}
}