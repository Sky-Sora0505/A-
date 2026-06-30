package jp.co.iterative.bus.frontend.service;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import jp.co.iterative.bus.entity.Reservation;
import jp.co.iterative.bus.entity.SeatReservation;
import jp.co.iterative.bus.frontend.form.ReserveForm;
import jp.co.iterative.bus.mapper.ReservationMapper;
import jp.co.iterative.bus.mapper.ReserveMapper;
import jp.co.iterative.bus.mapper.SeatReservationMapper;

@Service
public class ReserveServiceImpl implements ReserveService {

    @Autowired
    private ReserveMapper reserveMapper;

    @Autowired
    private ReservationMapper reservationMapper;

    @Autowired
    private SeatReservationMapper seatReservationMapper;


    @Override
    public void populateSeatSelectInfo(ReserveForm form) {
        Map<String, Object> routeDetail = reserveMapper.selectRouteDetail(form.getRouteId());
        if (routeDetail != null) {
            form.setDepartureBusStopName((String) routeDetail.get("departure_bus_stop_name"));
            form.setArrivalBusStopName((String) routeDetail.get("arrival_bus_stop_name"));
            form.setPrice((Integer) routeDetail.get("price"));
            form.setRowNum((Integer) routeDetail.get("row_num"));
            form.setColumnNum((Integer) routeDetail.get("column_num"));
        }
        List<String> reservedSeats = reserveMapper.selectReservedSeats(form.getRouteId(), form.getRideDate());
        form.setReservedSeats(reservedSeats);
    }


    @Override
    @Transactional
    public void registerReservation(ReserveForm form) {


        List<String> selectedSeats = form.getSelectedSeats();
        if (selectedSeats == null || selectedSeats.isEmpty()) {
            return;
        }


        Reservation reservation = new Reservation();
        reservation.setRouteId(form.getRouteId());
        reservation.setRideDate(form.getRideDate());


        reservation.setMemberId(0);


        reservationMapper.insertSelective(reservation);


        Integer newReservationId = reservation.getId();


        for (String seatName : selectedSeats) {
            SeatReservation seatDetail = new SeatReservation();

            seatDetail.setReservationId(newReservationId);
            seatDetail.setSeatName(seatName);


            seatReservationMapper.insertSelective(seatDetail);
        }
    }
}