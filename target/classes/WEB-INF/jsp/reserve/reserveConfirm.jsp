<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/jsp/common/define.jsp"%>
<%@ taglib prefix="fn" uri="http://java.sun.com/jsp/jstl/functions"%>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>予約確認</title>
<style type="text/css">
.left-1x {
	text-align: left;
	width: 100px;
	background-color: #ADD8E6;
}
</style>
</head>
<body>
	<h1>予約確認</h1>
	<table border="1"
		style="border-collapse: collapse; border-color: #000;">
		<tr>
			<th class="left-1x">日付</th>
			<td>
				<%--日付(yyyy年MM月dd日)を出力--%>
				<fmt:formatDate value="${reserveForm.rideDate}" pattern="yyyy年MM月dd日"/>
			</td>
		</tr>
		<tr>
			<th class="left-1x">出発</th>
			<td>
				<c:out value="${reserveForm.departureBusStopName}" />
				(<c:out value="${reserveForm.departureTime}" />)
			</td>
		</tr>
		<tr>
			<th class="left-1x">到着</th>
			<td>
				<c:out value="${reserveForm.arrivalBusStopName}" />
				(<c:out value="${reserveForm.arrivalTime}" />)
			</td>
		</tr>
	</table>

	<br>

	<table style="border-collapse: collapse;">
		<tr style="border-bottom: 2px solid #333;">
			<th style="text-align: left;" width="200px">1席あたりの料金</th>
			<td>
				<%--1席あたりの料金を記入 --%>
				&yen;<fmt:formatNumber value="${reserveForm.price}" pattern="#,###"/>
			</td>
		</tr>
	</table>

	<br>

	<table border="1"
		style="border-collapse: collapse; border-color: #000;">
		<tr>
			<th class="left-1x">座席</th>
			<td>
				<%-- 座席番号をカンマ区切りで表示 --%>
				<c:forEach items="${reserveForm.selectedSeats}" var="reserveSeat" varStatus="status">
					<c:out value="${reserveSeat}"/><c:if test="${!status.last}">, </c:if>
				</c:forEach>
			</td>
		</tr>
	</table>

	<br>

	<table style="border-collapse: collapse;">
		<tr style="border-bottom: 2px solid #333;">
			<th style="text-align: left;" width="200px">小計</th>
			<td>
				<%--小計を記入 --%>
				&yen;
				<fmt:formatNumber value="${totalAmount}" pattern="#,###"/>
			</td>
		</tr>
	</table>

	<p>上記で予約します。よろしいですか？</p>

	<form:form modelAttribute="reserveForm">
		<form:hidden path="routeId"/>
		<form:hidden path="rideDate"/>
		<form:hidden path="departureBusStopName"/>
		<form:hidden path="departureTime"/>
		<form:hidden path="arrivalBusStopName"/>
		<form:hidden path="arrivalTime"/>
		<form:hidden path="price"/>
		<c:forEach items="${reserveForm.selectedSeats}" var="seat" varStatus="status">
			<input type="hidden" name="selectedSeats[${status.index}]" value="${seat}" />
		</c:forEach>

		<input type="submit" value="ＯＫ" formaction="regist"
			style="margin-right: 50px; width: 100px">
		<input type="submit" value="戻る" formaction="seatSelect"
			style="margin-right: 50px; width: 100px">
	</form:form>
</body>
</html>