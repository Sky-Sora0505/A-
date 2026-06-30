package jp.co.iterative.bus.frontend.form;

import java.util.Date;

import org.springframework.format.annotation.DateTimeFormat;


public class RouteToReserveForm {
	private Integer id;
	@DateTimeFormat(pattern = "yyyyMMdd")
	private Date rideDate;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Date getRideDate() {
		return rideDate;
	}

	public void setRideDate(Date rideDate) {
		this.rideDate = rideDate;
	}

}
