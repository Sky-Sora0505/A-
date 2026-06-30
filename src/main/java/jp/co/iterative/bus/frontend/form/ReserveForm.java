package jp.co.iterative.bus.frontend.form;

import java.util.Date;
import java.util.List;

import javax.validation.constraints.NotNull;

import org.springframework.format.annotation.DateTimeFormat;



public class ReserveForm {

    @NotNull
    private Integer routeId;

    @NotNull
    @DateTimeFormat(pattern = "yyyyMMdd")
    private Date rideDate;

    // 画面表示用フィールド
    private String departureBusStopName;
    private String arrivalBusStopName;
    private Integer price;
    private Integer rowNum;
    private Integer columnNum;
    private String departureTime;
    private String arrivalTime;


    // 入力・状態管理用
    private List<String> selectedSeats;
    private List<String> reservedSeats;
	public Integer getRouteId() {
		return routeId;
	}
	public void setRouteId(Integer routeId) {
		this.routeId = routeId;
	}
	public Date getRideDate() {
		return rideDate;
	}
	public void setRideDate(Date rideDate) {
		this.rideDate = rideDate;
	}
	public String getDepartureBusStopName() {
		return departureBusStopName;
	}
	public void setDepartureBusStopName(String departureBusStopName) {
		this.departureBusStopName = departureBusStopName;
	}
	public String getArrivalBusStopName() {
		return arrivalBusStopName;
	}
	public void setArrivalBusStopName(String arrivalBusStopName) {
		this.arrivalBusStopName = arrivalBusStopName;
	}
	public Integer getPrice() {
		return price;
	}
	public void setPrice(Integer price) {
		this.price = price;
	}
	public Integer getRowNum() {
		return rowNum;
	}
	public void setRowNum(Integer rowNum) {
		this.rowNum = rowNum;
	}
	public Integer getColumnNum() {
		return columnNum;
	}
	public void setColumnNum(Integer columnNum) {
		this.columnNum = columnNum;
	}
	public List<String> getSelectedSeats() {
		return selectedSeats;
	}
	public void setSelectedSeats(List<String> selectedSeats) {
		this.selectedSeats = selectedSeats;
	}
	public List<String> getReservedSeats() {
		return reservedSeats;
	}
	public void setReservedSeats(List<String> reservedSeats) {
		this.reservedSeats = reservedSeats;
	}
	public String getDepartureTime() {
		return departureTime;
	}
	public void setDepartureTime(String departureTime) {
		this.departureTime = departureTime;
	}
	public String getArrivalTime() {
		return arrivalTime;
	}
	public void setArrivalTime(String arrivalTime) {
		this.arrivalTime = arrivalTime;
	}






}