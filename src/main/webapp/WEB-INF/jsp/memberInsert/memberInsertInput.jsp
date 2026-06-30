<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@ include file="/WEB-INF/jsp/common/define.jsp"%>
<jsp:include page="/WEB-INF/jsp/common/header.jsp" />

<div id="section">
	<div id="article">
		<form:form modelAttribute="memberInsertForm" action="confirm"
			method="post">
			<form:errors path="name" element="p" cssClass="error" />
			<form:errors path="loginId" element="p" cssClass="error" />
			<form:errors path="tel" element="p"/>
			<form:errors path="mailAddress" element="p"/>


			<div>
				<label>氏名</label><br>
				<form:input path="name" />
			</div>

			<div>
				<label>会員ID</label><br>
				<form:input path="loginId" />
			</div>

			<div>
				<label>パスワード</label><br>
				<form:password path="password" />
			</div>

			<div>
				<label>電話番号</label><br>
				<form:input path="tel1" size="4" maxlength="4" />
				-
				<form:input path="tel2" size="4" maxlength="4" />
				-
				<form:input path="tel3" size="4" maxlength="4" />

			</div>

			<div>
				<label>メールアドレス</label><br>
				<form:input path="mailAddress1" size="20" />
				@
				<form:input path="mailAddress2" size="20" />

			</div>

			<div>
				<input type="submit" value="会員登録" formaction="confirm" />
			</div>

		</form:form>
	</div>
</div>