package jp.co.iterative.bus.frontend.service;

import jp.co.iterative.bus.frontend.form.ReserveForm;

public interface ReserveService {
    /**
     * 座席選択画面に必要な情報を取得し、Formにセットする
     */
    void populateSeatSelectInfo(ReserveForm form);

    void registerReservation(ReserveForm form);
}