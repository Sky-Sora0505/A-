package jp.co.iterative.bus.frontend.controller;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

import javax.validation.Valid;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.RequestMapping;

import jp.co.iterative.bus.entity.BusStop;
import jp.co.iterative.bus.entity.BusStopExample;
import jp.co.iterative.bus.entity.RouteCustomized;
import jp.co.iterative.bus.frontend.form.RouteSearchForm;
import jp.co.iterative.bus.frontend.form.RouteToReserveForm;
import jp.co.iterative.bus.frontend.security.MemberDetails;
import jp.co.iterative.bus.mapper.BusStopMapper;
import jp.co.iterative.bus.mapper.RouteCustomMapper;

@Controller
@RequestMapping("/routeSearch")
public class RouteSearchController {
	@Autowired
	private BusStopMapper busStopMapper;
	@Autowired
	private RouteCustomMapper routeCustomMapper;

	@ModelAttribute
	public RouteSearchForm createForm() {
		return new RouteSearchForm();
	}
	@RequestMapping("/index")
	public String index(Model model,@AuthenticationPrincipal MemberDetails memberDetails) {

		prepareDate(model);

		stopAcquisition(model);
		return "route/routeSearch";
	}

	@RequestMapping("/search")

	public String search(@Valid RouteSearchForm routeSearchForm,BindingResult bindingResult,
			RouteToReserveForm routeToReserveForm, Model model,@AuthenticationPrincipal MemberDetails memberDetails) {
		if(bindingResult.hasErrors()) {
			return index(model, memberDetails);
		}
		// 停留所を取得する
		stopAcquisition(model);
		//今年と来年表示
		prepareDate(model);

		Calendar calendar = Calendar.getInstance();
		calendar.clear();
		Date rideDate = null;
		List<RouteCustomized> routeList = new ArrayList<>();
		if (routeSearchForm.getYear() != null && routeSearchForm.getMonth() != null && routeSearchForm.getDay() != null) {
			calendar.set(routeSearchForm.getYear(), routeSearchForm.getMonth() - 1, routeSearchForm.getDay());
			rideDate = calendar.getTime();
			routeList = routeCustomMapper.routeSearch(rideDate, routeSearchForm.getDepartureBusStopId(),routeSearchForm.getArrivalBusStopId());
		}
		if(routeList.isEmpty()) {
			model.addAttribute("errorNotExist", "該当する情報が存在しませんでした。");
		}
		model.addAttribute("rideDate", rideDate);
		model.addAttribute("routeList", routeList);
		return "route/routeSearch";
	}
	private void prepareDate(Model model){
		Calendar calendar = Calendar.getInstance();
		int currentYear = calendar.get(Calendar.YEAR);
		List<Integer> yearList = new ArrayList<>();
		for (int i = 0; i <= 1; i++) {
			yearList.add(currentYear + i);
		}
		model.addAttribute("yearList", yearList);
	}
	private void stopAcquisition(Model model) {
		BusStopExample busStopExample = new BusStopExample();
		busStopExample.setOrderByClause("id");
		List<BusStop> busStopList = busStopMapper.selectByExample(busStopExample);

		model.addAttribute("busStopList", busStopList);
	}
}
