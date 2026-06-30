package jp.co.iterative.bus.frontend.form;

import javax.validation.constraints.NotNull;

public class RouteSearchForm {


	@NotNull(message = "年を選択してください。")
	private Integer year;
	@NotNull(message = "月を選択してください。")
	private Integer month;
	@NotNull(message = "日を選択してください。")
	private Integer day;
	private Integer departureBusStopId;
	private Integer arrivalBusStopId;

	public Integer getYear() {
		return year;
	}

	public void setYear(Integer year) {
		this.year = year;
	}

	public Integer getMonth() {
		return month;
	}

	public void setMonth(Integer month) {
		this.month = month;
	}

	public Integer getDay() {
		return day;
	}

	public void setDay(Integer day) {
		this.day = day;
	}

	public Integer getDepartureBusStopId() {
		return departureBusStopId;
	}

	public void setDepartureBusStopId(Integer departureBusStopId) {
		this.departureBusStopId = departureBusStopId;
	}

	public Integer getArrivalBusStopId() {
		return arrivalBusStopId;
	}

	public void setArrivalBusStopId(Integer arrivalBusStopId) {
		this.arrivalBusStopId = arrivalBusStopId;
	}

}
