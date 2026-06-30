<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@ include file="/WEB-INF/jsp/common/define.jsp"%>
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
		<h1>予約削除確認</h1>
		<table border="1"
			style="border-collapse: collapse; border-color: #000;">
			<tr>
				<th class="left-1x">日付</th>
				<td>
					<fmt:formatDate value="${reservation.rideDate}" pattern="yyyy年MM月dd日"/>
				</td>
			</tr>
			<tr>
				<th class="left-1x">出発</th>
				<td>
					<c:out value="${reservation.departureBusStopName}" />
					(<fmt:formatDate value="${reservation.departureTime}" pattern="HH:mm" />)
				</td>
			</tr>
			<tr>
				<th class="left-1x">到着</th>
				<td>
					<c:out value="${reservation.arrivalBusStopName}" />
					(<fmt:formatDate value="${reservation.arrivalTime}" pattern="HH:mm" />)
				</td>
			</tr>
		</table>

		<br>

		<table style="border-collapse: collapse;">
			<tr style="border-bottom: 2px solid #333;">
				<th style="text-align: left;" width="200px">1席あたりの料金</th>
				<td>
					&yen;<fmt:formatNumber value="${reservation.price}" pattern="#,###"/>
				</td>
			</tr>
		</table>

		<br>

		<table border="1"
			style="border-collapse: collapse; border-color: #000;">
			<tr>
				<th class="left-1x">座席</th>
				<td>
					<c:forEach items="${reservation.seatNames}" var="seat" varStatus="status">
						<c:out value="${seat}"/><c:if test="${!status.last}">, </c:if>
					</c:forEach>
				</td>
			</tr>
		</table>

		<br>

		<table style="border-collapse: collapse;">
			<tr style="border-bottom: 2px solid #333;">
				<th style="text-align: left;" width="200px">小計</th>
				<td>
					&yen;<fmt:formatNumber value="${totalAmount}" pattern="#,###"/>
				</td>
			</tr>
		</table>

		<p>上記の予約を削除します。よろしいですか？</p>

		<form:form modelAttribute="reserveDeleteForm" method="post">
			<form:hidden path="reservationId" />

			<input type="submit" value="ＯＫ" formaction="delete" style="margin-right: 50px; width: 100px">
			<input type="submit" value="戻る" formaction="list" formmethod="get" style="margin-right: 50px; width: 100px">
		</form:form>
	</div>
