<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/jsp/common/define.jsp"%>

<jsp:include page="/WEB-INF/jsp/common/header.jsp"></jsp:include>

<div id="section">
	<div id="article">

${SPRING_SECURITY_LAST_EXCEPTION.message}
	<h1>ログイン</h1>
	<form:form modelAttribute="loginForm" action="auth">
	<form:errors path="*"/>
	<dl>
		<dt>ログインID</dt>
		<dd><form:input path="username"/></dd>
		<dt>パスワード</dt>
		<dd><form:password path="password"/></dd>
	</dl>
	<input type="submit" value="ログイン" class="btn">
	</form:form>

	</div>
</div>
<jsp:include page="/WEB-INF/jsp/common/footer.jsp"></jsp:include>
