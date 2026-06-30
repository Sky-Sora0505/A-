<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@include file="/WEB-INF/jsp/common/define.jsp"%>

<jsp:include page="/WEB-INF/jsp/common/header.jsp"></jsp:include>

<div id="section">
	<div id="article">
		<h2>会員登録確認</h2>
		<p>以下の内容で登録します。よろしいですか？</p>
		<fieldset style="width: 310px;">
			<legend>会員情報</legend>
			<div>
				<div style="display: inline-flex;">
					<div style="margin-right: 50px">

						<div>氏名</div>
						<c:out value="${memberInsertForm.name}" />
					</div>
				</div>
			</div>
			<div>
				<div style="display: inline-flex;">
					<div style="margin-right: 50px">
						<div>会員ID</div>
						<c:out value="${memberInsertForm.loginId}" />
					</div>
				</div>
			</div>
			<div>
				<div>パスワード</div>
				<span style="-webkit-text-security: disc;"><c:out
						value="${memberInsertForm.password}" /></span>
			</div>
			<div>
				<div>電話番号</div>
				<c:out value="${memberInsertForm.tel1}" />
				-
				<c:out value="${memberInsertForm.tel2}" />
				-
				<c:out value="${memberInsertForm.tel3}" />
			</div>
			<div>
				<div>メールアドレス</div>
				<c:out value="${memberInsertForm.mailAddress1}" />
				@
				<c:out value="${memberInsertForm.mailAddress2}" />
			</div>
			<form:form modelAttribute="memberInsertForm">
				<form:hidden path="name" />
				<form:hidden path="loginId" />
				<form:hidden path="password" />
				<form:hidden path="tel1" />
				<form:hidden path="tel2" />
				<form:hidden path="tel3" />
				<form:hidden path="mailAddress1" />
				<form:hidden path="mailAddress2" />
				<br>
				<input type="submit" value="ＯＫ" formaction="insert">
				<input type="submit" value="戻る" formaction="input">
			</form:form>
		</fieldset>
	</div>
</div>
<jsp:include page="/WEB-INF/jsp/common/footer.jsp"></jsp:include>
