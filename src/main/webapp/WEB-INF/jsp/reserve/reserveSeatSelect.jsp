<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<%@ taglib prefix="fn" uri="http://java.sun.com/jsp/jstl/functions"%>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt"%>

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>座席指定</title>
<style>
.underline-black {
	text-decoration: underline;
	text-decoration-color: black;
}

.info-table {
	border-collapse: collapse;
	margin-bottom: 20px;
}

.info-table th, .info-table td {
	border: 1px solid #000;
	padding: 5px 10px;
}

.info-table th {
	background-color: #ADD8E6;
	width: 80px;
	text-align: center;
}

.seat-grid {
	border-collapse: collapse;
	margin-top: 20px;
	text-align: center;
}

.seat-grid th, .seat-grid td {
	border: 1px solid #999;
	padding: 0;
}

.header-cell {
	background-color: #ADD8E6;
	padding: 5px;
	min-width: 30px;
}





.driver-seat {
	background-color: #ADD8E6;
	width: 60px;
	writing-mode: vertical-rl;
	text-align: center;
	vertical-align: middle;
}





.driver-seat-empty {
	width: 60px;
	background-color: #ADD8E6;
}

.seat-cell {
	width: 50px;
	height: 50px;
	background-color: #B0C4DE;
}

.seat-box {
	width: 30px;
	height: 30px;
	margin: 0 auto;
	background-color: #fff;
	border: 3px solid #000;
	display: flex;
	align-items: center;
	justify-content: center;
	font-weight: bold;
}

.reserved .seat-box {
	border-color: #666;
	color: #666;
	background-color: #eee;
}

.seat-checkbox {
	display: none;
}

.seat-checkbox:checked+.seat-box {
	background-color: #FFEB3B;
}
.reserve-btn {
	background-color: #a0a0a0;
	border: 1px solid #333;
	padding: 4px 12px;
	cursor: pointer;
}
.button-group {
	display: flex;
	justify-content: center;
	gap: 20px;
	margin-top: 10px;
}
</style>
</head>
<body>

	<h2>座席指定</h2>





	<table class="info-table">
		<tr>
			<th>日付</th>
			<td><fmt:formatDate value="${reserveForm.rideDate}"
					pattern="yyyy年MM月dd日" /></td>
		</tr>
		<tr>
			<th>出発</th>
			<td>
				<c:out value="${routeCustomized.departureName}" />
				(<fmt:formatDate value="${routeCustomized.departureTime}" pattern="HH:mm" />)
			</td>
		</tr>
		<tr>
			<th>到着</th>
			<td>
				<c:out value="${routeCustomized.arrivalName}" />
				(<fmt:formatDate value="${routeCustomized.arrivalTime}" pattern="HH:mm" />)
			</td>
		</tr>
	</table>

	<div class="price-area">
		<p class="underline-black">
			1席あたりの料金:
			<fmt:formatNumber value="${routeCustomized.price}" pattern="￥#,###" />
		</p>
	</div>
	<form id="reserveForm" action="/reserve/confirm">
		<input type="hidden" name="routeId" value="${reserveForm.routeId}">
		<input type="hidden" name="rideDate"
			value="<fmt:formatDate value='${reserveForm.rideDate}' pattern='yyyyMMdd' />">
		<input type="hidden" name="price" value="${reserveForm.price}">

		<input type="hidden" name="departureBusStopName" value="${routeCustomized.departureName}">
		<input type="hidden" name="arrivalBusStopName" value="${routeCustomized.arrivalName}">
		<input type="hidden" name="departureTime" value="<fmt:formatDate value='${routeCustomized.departureTime}' pattern='HH:mm' />">
<input type="hidden" name="arrivalTime" value="<fmt:formatDate value='${routeCustomized.arrivalTime}' pattern='HH:mm' />">



		<p>予約する座席を選択して、予約ボタンを押下してください。</p>
		<c:if test="${not empty errorMessage}">
			<div class="error-message">
				<c:out value="${errorMessage}" />
			</div>
		</c:if>

	<c:set var="alphabet" value="ABCDEFGHIJKLMNOPQRSTUVWXYZ" />
		<c:set var="rowNum" value="${routeCustomized.rowNum}" />
		<c:set var="colNum" value="${routeCustomized.columnNum}" />



		<fmt:parseNumber var="topSpan" value="${(colNum + 1) / 2}" integerOnly="true" />
		<c:set var="bottomSpan" value="${colNum - topSpan}" />

		<div style="overflow-x: auto;">
			<table class="seat-grid">
				<tr>
					<th class="header-cell" style="width:60px;"></th>

					<c:forEach var="c" begin="1" end="${rowNum}" step="1">
						<th class="header-cell"><c:out value="${c}" /></th>
					</c:forEach>

					<th class="header-cell"></th>
				</tr>

				<c:forEach var="r" begin="1" end="${colNum}" step="1">
					<tr>
						<c:if test="${r == 1}">
							<td rowspan="${topSpan}" class="driver-seat">
								<div class="driver-seat-inner">運転席</div>
							</td>
						</c:if>
						<c:if test="${bottomSpan > 0 and r == (topSpan + 1)}">
							<td rowspan="${bottomSpan}" class="driver-seat-empty"></td>
						</c:if>

						<c:set var="letterIndex" value="${colNum - r}" />
						<c:set var="rowLetter" value="${fn:substring(alphabet, letterIndex, letterIndex + 1)}" />

						<c:forEach var="c" begin="1" end="${rowNum}" step="1">
							<c:set var="seatId" value="${rowLetter}-${c}" />

							<td class="seat-cell">
								<c:choose>
									<c:when test="${not empty reservedSeatsList and reservedSeatsList.contains(seatId)}">
										<div class="reserved" aria-hidden="true">
											<div class="seat-box" role="img" aria-label="${seatId} 予約済み">×</div>
										</div>
									</c:when>
									<c:otherwise>
										<label>
											<input type="checkbox"
												name="selectedSeats"
												value="${seatId}"
												class="seat-checkbox"
												aria-label="${seatId} 座席"
												<c:if test="${not empty selectedSeatsList and selectedSeatsList.contains(seatId)}">checked="checked"</c:if> />
											<div class="seat-box"></div>
										</label>
									</c:otherwise>
								</c:choose>
							</td>
						</c:forEach>

						<td class="header-cell"><c:out value="${rowLetter}" /></td>
					</tr>
				</c:forEach>
			</table>
		</div>
		<br>
		<div class="button-group">
			<button type="submit" class="reserve-btn">予約</button>
			<input type="submit" value="戻る" class="reserve-btn" formaction="/routeSearch/index">
		</div>
	</form>
	</form>

</body>
</html>