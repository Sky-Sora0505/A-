package jp.co.iterative.bus.frontend.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import jp.co.iterative.bus.entity.Reservation;
import jp.co.iterative.bus.entity.RouteCustomized;
import jp.co.iterative.bus.entity.SeatReservation;
import jp.co.iterative.bus.frontend.form.ReserveForm;
import jp.co.iterative.bus.frontend.form.RouteToReserveForm;
import jp.co.iterative.bus.frontend.service.ReserveService;
import jp.co.iterative.bus.mapper.ReservationMapper;
import jp.co.iterative.bus.mapper.RouteCustomMapper;
import jp.co.iterative.bus.mapper.SeatReservationMapper;

@Controller
@RequestMapping("reserve")
public class ReserveController {

	@Autowired
	private ReserveService reserveService;

	@Autowired
	private ReservationMapper reservationMapper;

	@Autowired
	private SeatReservationMapper seatReservationMapper;

	@Autowired
	private RouteCustomMapper routeCustomMapper;

	@RequestMapping("seatSelect")
	public String seatSelect(ReserveForm reserveForm, RouteToReserveForm routeToReserveForm, Model model, RedirectAttributes redirectAttributes) {

		// 1. 路線IDの取得（検索画面から来た場合と、確認画面から戻ってきた場合の両方に対応）
		if (routeToReserveForm.getId() != null) {
		    reserveForm.setRouteId(routeToReserveForm.getId());
		}


		Integer targetRouteId = reserveForm.getRouteId();
		// 2. 搭乗日の取得
		if (routeToReserveForm.getRideDate() != null) {
			reserveForm.setRideDate(routeToReserveForm.getRideDate());
		}

		if (targetRouteId != null) {
			// 3. 路線情報の取得
			RouteCustomized routeCustomized = routeCustomMapper.selectCustomByPrimaryKey(targetRouteId);

			// 4. 予約状況（すでに取られている座席）の取得
			reserveService.populateSeatSelectInfo(reserveForm);
			List<String> reservedSeatsList = reserveForm.getReservedSeats();

			// 5. 満席チェック処理
			int totalSeats = routeCustomized.getRowNum() * routeCustomized.getColumnNum();
			if (reservedSeatsList != null && reservedSeatsList.size() >= totalSeats) {
				// 満席の場合は検索画面へリダイレクト
				redirectAttributes.addFlashAttribute("errorMessage", "指定された路線は満席になりました。別の路線を検索しなおしてください。");
				return "redirect:/routeSearch/index";
			}

			// 6. JSPで表示するための情報をModelに登録
			model.addAttribute("routeCustomized", routeCustomized);
			model.addAttribute("reservedSeatsList", reservedSeatsList);
		}

		// 7. 選択済みの座席状態などを維持するため、reserveFormをModelに登録
		model.addAttribute("reserveForm", reserveForm);

		return "reserve/reserveSeatSelect";
	}

	@RequestMapping("confirm")
	public String confirm(ReserveForm reserveForm, Model model, RedirectAttributes redirectAttributes) {

		RouteCustomized routeCustomized = routeCustomMapper.selectCustomByPrimaryKey(reserveForm.getRouteId());

		if (reserveForm.getSelectedSeats() == null || reserveForm.getSelectedSeats().isEmpty()) {
			model.addAttribute("errorMessage", "座席を選択してください。");
			model.addAttribute("routeCustomized", routeCustomized);

			reserveService.populateSeatSelectInfo(reserveForm);

			model.addAttribute("reservedSeatsList", reserveForm.getReservedSeats());
			model.addAttribute("reserveForm", reserveForm);

			return "reserve/reserveSeatSelect";
		}

		reserveService.populateSeatSelectInfo(reserveForm);
		List<String> latestReservedSeats = reserveForm.getReservedSeats();

		if (latestReservedSeats != null) {
			for (String selectedSeat : reserveForm.getSelectedSeats()) {
				if (latestReservedSeats.contains(selectedSeat)) {

					int totalSeats = routeCustomized.getRowNum() * routeCustomized.getColumnNum();
					if (latestReservedSeats.size() >= totalSeats) {
						redirectAttributes.addFlashAttribute("errorMessage", "指定された路線は満席になりました。別の路線を検索しなおしてください。");

						return "redirect:/routeSearch/index";
					}

					model.addAttribute("errorMessage", "指定した座席が他の利用者によって予約されました。再度指定しなおしてください。");
					model.addAttribute("routeCustomized", routeCustomized);
					model.addAttribute("rideDate", reserveForm.getRideDate());
					model.addAttribute("reservedSeatsList", latestReservedSeats);
					model.addAttribute("reserveForm", reserveForm);

					return "reserve/reserveSeatSelect";
				}
			}
		}

		int totalAmount = reserveForm.getPrice() * reserveForm.getSelectedSeats().size();
		model.addAttribute("totalAmount", totalAmount);

		model.addAttribute("reserveForm", reserveForm);

		return "reserve/reserveConfirm";
	}

	@RequestMapping("regist")
	public String regist(ReserveForm reserveForm, RedirectAttributes redirectAttributes, Model model) {

		RouteCustomized routeCustomized = routeCustomMapper.selectCustomByPrimaryKey(reserveForm.getRouteId());


		reserveService.populateSeatSelectInfo(reserveForm);
		List<String> latestReservedSeats = reserveForm.getReservedSeats();

		if (latestReservedSeats != null && reserveForm.getSelectedSeats() != null) {
			for (String selectedSeat : reserveForm.getSelectedSeats()) {
				if (latestReservedSeats.contains(selectedSeat)) {


					int totalSeats = routeCustomized.getRowNum() * routeCustomized.getColumnNum();
					if (latestReservedSeats.size() >= totalSeats) {
						redirectAttributes.addFlashAttribute("errorMessage", "指定された路線は満席になりました。別の路線を検索しなおしてください。");
						return "redirect:/routeSearch/index";
					}


					model.addAttribute("errorMessage", "指定した座席が他の利用者によって予約されました。再度指定しなおしてください。");
					model.addAttribute("routeCustomized", routeCustomized);
					model.addAttribute("rideDate", reserveForm.getRideDate());
					model.addAttribute("reservedSeatsList", latestReservedSeats);
					model.addAttribute("reserveForm", reserveForm);

					return "reserve/reserveSeatSelect";
				}
			}
		}


		Reservation reservation = new Reservation();
		reservation.setMemberId(1);
		reservation.setRideDate(reserveForm.getRideDate());
		reservation.setRouteId(reserveForm.getRouteId());

		reservationMapper.insertSelective(reservation);

		if (reserveForm.getSelectedSeats() != null) {
			for (String seatName : reserveForm.getSelectedSeats()) {
				SeatReservation seatReservation = new SeatReservation();
				seatReservation.setReservationId(reservation.getId());
				seatReservation.setSeatName(seatName);

				seatReservationMapper.insertSelective(seatReservation);
			}
		}

		int totalAmount = 0;
		if (reserveForm.getSelectedSeats() != null) {
			totalAmount = reserveForm.getPrice() * reserveForm.getSelectedSeats().size();
		}

		redirectAttributes.addFlashAttribute("reserveForm", reserveForm);
		redirectAttributes.addFlashAttribute("totalAmount", totalAmount);

		return "redirect:/reserve/complete";
	}

	@RequestMapping("complete")
	public String complete(ReserveForm reserveForm, Model model) {
		return "reserve/reserveComplete";
	}

}