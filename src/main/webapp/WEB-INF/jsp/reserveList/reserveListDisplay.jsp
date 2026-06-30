<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ include file="/WEB-INF/jsp/common/define.jsp" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt"%>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>予約一覧</title>
<style type="text/css">
	th { background-color: #ADD8E6; padding: 8px; }
	td { padding: 8px; }
</style>
</head>
<body>
	<jsp:include page="/WEB-INF/jsp/common/header.jsp" />

	<div>
		<h1>予約一覧</h1>

		<c:if test="${not empty errorMessage}">
			<c:out value="${errorMessage}"/>
		</c:if>

		<c:choose>
			<c:when test="${empty reservationList}">
				<p>現在、ご予約はありません。</p>
				<br>
				<form action="/routeSearch/index" method="get">
					<input type="submit" value="路線検索へ戻る" style="width: 150px;">
				</form>
			</c:when>

			<c:otherwise>
				<form action="deleteConfirm" method="post">
					<table border="1" style="border-collapse: collapse; border-color: #000;">
						<tr>
							<th>選択</th>
							<th>日付</th>
							<th>座席</th>
							<th>出発</th>
							<th>到着</th>
							<th>料金</th>

						</tr>

						<c:forEach items="${reservationList}" var="reservation">
							<tr>
								<td style="text-align: center;">
									<input type="radio" name="reservationId" value="${reservation.reservationId}">
								</td>
								<td><fmt:formatDate value="${reservation.rideDate}" pattern="yyyy年 MM月 dd日"/></td>
								<td>
									<c:forEach items="${reservation.seatNames}" var="seat" varStatus="status">
										<c:out value="${seat}"/><c:if test="${!status.last}">,</c:if>
									</c:forEach>
								</td>
								<td><c:out value="${reservation.departureBusStopName}" />(<fmt:formatDate value="${reservation.departureTime}" pattern="HH:mm" />)</td>
								<td><c:out value="${reservation.arrivalBusStopName}" />(<fmt:formatDate value="${reservation.arrivalTime}" pattern="HH:mm" />)</td>
								<td>&yen;<fmt:formatNumber
					value="${reservation.price}" pattern="#,###" /></td>
							</tr>
						</c:forEach>
					</table>

					<br>
					<input type="submit" value="削除" style="width: 100px;">
				</form>
			</c:otherwise>
		</c:choose>
	</div>
</body>
</html>
