<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<%@ include file="/WEB-INF/jsp/common/define.jsp" %>
<jsp:include page="/WEB-INF/jsp/common/header.jsp" />
<title>Insert title here</title>
<style type="text/css">
.left-1x {
	text-align: left;
	width: 100px;
	background-color: #ADD8E6;
}
</style>
<div>
	<h1>予約削除完了</h1>

	<c:if test="${not empty canceledReservation}">
		<%-- ① 日付・出発・到着のテーブル --%>
		<table border="1"
			style="border-collapse: collapse; border-color: #000;">
			<tr>
				<th class="left-1x">日付</th>
				<td><fmt:formatDate value="${canceledReservation.rideDate}"
						pattern="yyyy年 MM月 dd日" /></td>
			</tr>
			<tr>
				<th class="left-1x">出発</th>
				<td><c:out value="${canceledReservation.departureBusStopName}" /> (<fmt:formatDate
						value="${canceledReservation.departureTime}" pattern="HH:mm" />)</td>
			</tr>
			<tr>
				<th class="left-1x">到着</th>
				<td><c:out value="${canceledReservation.arrivalBusStopName}" /> (<fmt:formatDate
						value="${canceledReservation.arrivalTime}" pattern="HH:mm" />)</td>
			</tr>
		</table>

		<br>

		<%-- ② 1席あたりの料金 --%>
		<table style="border-collapse: collapse;">
			<tr style="border-bottom: 2px solid #333;">
				<th style="text-align: left;" width="180px">1席あたりの料金</th>
				<td style="text-align: right; width: 100px;">&yen;<fmt:formatNumber
						value="${canceledReservation.price}" pattern="#,###" />
				</td>
			</tr>
		</table>

		<br>

		<%-- ③ 座席 --%>
		<table border="1"
			style="border-collapse: collapse; border-color: #000;">
			<tr>
				<th class="left-1x">座席</th>
				<td style="width: 180px;"><c:forEach
						items="${canceledReservation.seatNames}" var="seat" varStatus="status">
						<c:out value="${seat}" />
						<c:if test="${!status.last}">、</c:if>
					</c:forEach></td>
			</tr>
		</table>

		<br>

		<%-- ④ 小計 --%>
		<table style="border-collapse: collapse;">
			<tr style="border-bottom: 2px solid #333;">
				<th style="text-align: left;" width="180px">小計</th>
				<td style="text-align: right; width: 100px;">&yen;<fmt:formatNumber
						value="${totalAmount}" pattern="#,###" />
				</td>
			</tr>
		</table>
	</c:if>

	<br>
	<p>予約の削除が完了しました。</p>

	<form action="/reserveList/list" method="get">
		<input type="submit" value="ＯＫ" style="margin-right: 50px; width: 100px">
	</form>
</div>
