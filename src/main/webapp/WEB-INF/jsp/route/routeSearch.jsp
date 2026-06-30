<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@ include file="/WEB-INF/jsp/common/define.jsp" %>
<jsp:include page="/WEB-INF/jsp/common/header.jsp" />
<style>
fieldset {
	border: 2px solid #000;
	border-radius: 4px;
	padding: 20px;
	width: fit-content;
	background-color: #fff;
}

legend {
	font-weight: bold;
	padding: 0 10px;
}

.date-select-group {
	margin-bottom: 20px;
}

.date-select-group select {
	padding: 4px;
	margin-right: 5px;
}

.route-select-container {
	display: flex;
	align-items: flex-end;
	gap: 15px;
	margin-bottom: 20px;
}

.select-box-group {
	display: flex;
	flex-direction: column;
	gap: 5px;
}

.select-box-group label {
	font-size: 14px;
	font-weight: bold;
}

.select-box-group select {
	padding: 6px;
	min-width: 120px;
}

.wave-separator {
	padding-bottom: 8px;
	font-weight: bold;
}

.search-btn-container {
	text-align: right;
}

.search-btn {
	background-color: #a0a0a0;
	border: 1px solid #333;
	padding: 6px 24px;
	cursor: pointer;
	font-weight: bold;
}

.result-table {
	border-collapse: collapse;
	width: auto;
	margin-top: 30px;
}

.result-table th {
	background-color: #add8e6;
	border: 1px solid #000;
	padding: 8px 12px;
	text-align: center;
}

.result-table td {
	border: 1px solid #000;
	padding: 8px 12px;
	vertical-align: bottom;
}

.align-top-right {
	vertical-align: top !important;
	text-align: right;
}

.align-center {
	vertical-align: middle !important;
	text-align: center;
}

.text-center {
	text-align: center;
}

.text-right {
	text-align: right;
}

.reserve-btn {
	background-color: #a0a0a0;
	border: 1px solid #333;
	padding: 4px 12px;
	cursor: pointer;
}

.sold-out-text {
	font-weight: bold;
	text-align: center;
}
</style>

<div id="section">
	<div id="article">
		<!-- 	髙橋作成 -->
		<c:if test="${not empty errorMessage}">
			<c:out value="${errorMessage}" />

		</c:if>

		<h1>路線検索</h1>
		<!-- 		日付の未選択などのバリデーションエラーを画面に一括表示する。 -->
		<c:if test="${not empty errorNotExist}">
			<c:out value="${errorNotExist}" />
		</c:if>
		<form:form modelAttribute="routeSearchForm">
			<form:errors path="year" element="p" />
			<form:errors path="month" element="p" />
			<form:errors path="day" element="p" />
		</form:form>
		<fieldset>
			<legend>検索条件</legend>
			<!-- Formと繋ぐ -->
			<form:form modelAttribute="routeSearchForm">
				<div class="date-select-group">
					<form:select path="year">
						<option value=""></option>
						<c:forEach var="y" items="${yearList}">
							<option value="${y}">${y}</option>
						</c:forEach>
					</form:select>
					年
					<form:select path="month">
						<option value=""></option>
						<c:forEach var="m" begin="1" end="12">
							<option value="${m}">${m}</option>
						</c:forEach>
					</form:select>
					月
					<form:select path="day">
						<option value=""></option>
						<c:forEach var="d" begin="1" end="31">
							<option value="${d}">${d}</option>
						</c:forEach>
					</form:select>
					日
				</div>
				<br>

				<div class="route-select-container">
					<div class="select-box-group">
						<label>出発地</label>
						<form:select path="departureBusStopId">
							<option value=""></option>
							<c:forEach var="busStop" items="${busStopList}">
								<option value="${busStop.id}">${busStop.name}</option>
							</c:forEach>
						</form:select>
					</div>

					<div class="wave-separator">～</div>
					<div class="select-box-group">
						<label>到着地</label>
						<form:select path="arrivalBusStopId">
							<option value=""></option>
							<c:forEach var="busStop" items="${busStopList}">
								<option value="${busStop.id}">${busStop.name}</option>
							</c:forEach>
						</form:select>
					</div>
				</div>

				<div class="search-btn-container">
					<!-- 				検索ボタンを押した時に、Controllerの /search メソッドへデータを届ける -->
					<input type="submit" value="検索" class="search-btn"
						formaction="/routeSearch/search">
				</div>
			</form:form>
		</fieldset>
	</div>
</div>
<c:if test="${not empty routeList}">


	<table class="result-table">
		<thead>
			<tr>
				<th style="width: 40px;">No.</th>
				<th style="width: 120px;">出発</th>
				<th style="width: 120px;">到着</th>
				<th style="width: 80px;">シート</th>
				<th style="width: 80px;">空席数</th>
				<th style="width: 100px;">料金</th>
				<th style="width: 100px;">予約</th>
			</tr>
		</thead>

		<c:forEach items="${routeList}" var="route" varStatus="status">
			<tr>
				<td class=align-top-right><c:out value="${status.count}" /></td>
				<td><c:out value="${route.departureName}" /><br> <fmt:formatDate
						value="${route.departureTime}" pattern="HH:mm" />発</td>
				<td><c:out value="${route.arrivalName}" /><br> <fmt:formatDate
						value="${route.arrivalTime}" pattern="HH:mm" />着</td>
				<td><c:out value="${route.columnNum}" />列</td>
				<!-- リアルタイムの空席数 -->
				<td class="text-right"><c:out value="${route.vacancyNumber}" /></td>


				<td class="text-right">￥<fmt:formatNumber pattern="#,###"
						value="${route.price}" /></td>
				<td class=align-center><form:form action="/reserve/seatSelect"
						modelAttribute="routeToReserveForm">
						<form:hidden path="id" value="${route.id}" />

						<fmt:formatDate value="${rideDate}" pattern="yyyyMMdd"
							var="fmtDate" />

						<input type="hidden" name="rideDate" value="${fmtDate}" />
						<!-- 検索結果のリストにデータが1件以上ある時だけ、予約をする表示する -->
						<c:choose>
							<c:when test="${route.vacancyNumber > 0}">
								<input type="submit" value="予約する" class="reserve-btn" />
							</c:when>
							<c:otherwise>
								<span class="sold-out-text">満席</span>
							</c:otherwise>
						</c:choose>
					</form:form></td>

			</tr>
		</c:forEach>
	</table>

</c:if>

</html>