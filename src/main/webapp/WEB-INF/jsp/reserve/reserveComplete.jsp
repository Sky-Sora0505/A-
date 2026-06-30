<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/jsp/common/define.jsp"%>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Insert title here</title>
<style type="text/css">
.left-1x {
	text-align: left;
	width: 100px;
	background-color: #ADD8E6;
}
</style>
</head>
<body>
	<h1>予約完了</h1>
	<table border="1"
		style="border-collapse: collapse; border-color: #000;">
		<tr>
			<th class="left-1x">日付</th>
			<td>
				<%--日付(yyyy年MM月dd日)を記入< --%>
				<fmt:formatDate value="${reserveForm.rideDate}" pattern="yyyy年MM月dd日"/>
			</td>
		</tr>
		<tr>
			<th class="left-1x">出発</th>
			<td>
				<%--出発地(出発時間)を記入 --%>
				<c:out value="${reserveForm.departureBusStopName}" />(<c:out value="${reserveForm.departureTime}" />)
			</td>
		</tr>
		<tr>
			<th class="left-1x">到着</th>
			<td>
				<%--到着地(到着時間)を記入 --%>
				<c:out value="${reserveForm.arrivalBusStopName}" />(<c:out value="${reserveForm.arrivalTime}" />)
			</td>
		</tr>
		<tr>
			<th class="left-1x">座席</th>
			<td>
				<%--座席を記入 --%>
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

	<br>

	<p>予約が完了しました。この画面を印刷して当日持参してください。</p>

	<form:form>
		<input type="submit" value="ＯＫ" formaction="/routeSearch/index"
			style="margin-right: 50px; width: 100px">
	</form:form>
</body>
</html>