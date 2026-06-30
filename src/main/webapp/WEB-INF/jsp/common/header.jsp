<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<%@taglib prefix="sec" uri="http://www.springframework.org/security/tags"%>

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>ヘッダー</title>
<style>
/* ヘッダー全体のコンテナ（横いっぱいに広げて要素を左右に分ける） */
#header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 15px 30px;
	background-color: #ffffff;
	box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); /* 下部にうっすら影 */
}

/* ロゴのスタイル */
#header .logo img {
	height: 40px; /* ロゴの大きさを適度に固定 */
	display: block;
}

/* 右側ナビゲーション全体の並び（横並び、間隔調整） */
#header .nav-menu {
	display: flex;
	align-items: center;
	gap: 20px; /* リンク同士の間隔 */
}

/* ログイン時の「〇〇様」のテキスト */
#header .user-name {
	font-weight: bold;
	color: #333333;
	margin-right: 10px;
}

/* リンクボタンの共通スタイル */
#header .nav-menu a {
	text-decoration: none;
	color: #4a5568;
	font-weight: 500;
	padding: 8px 16px;
	border-radius: 4px;
	transition: background-color 0.2s, color 0.2s;
}

/* マウスを乗せたときの変化 */
#header .nav-menu a:hover {
	background-color: #f7fafc;
	color: #3182ce; /* 爽やかな青色に */
}

/* ログインボタンなど、特定のボタンを目立たせるアクセント（お好みで） */
#header .nav-menu a.btn-primary {
	background-color: #3182ce;
	color: #ffffff;
}
#header .nav-menu a.btn-primary:hover {
	background-color: #2b6cb0;
	color: #ffffff;
}
#header .nav-menu a.btn-secondary:hover{
	background-color: #ff0000;
	color: #ffffff;
}

</style>
</head>
<body>
	<div id="header">
		<div class="logo">
			<a href="/routeSearch/index">
				<img src="/images/logo_k.jpg" alt="ロゴ">
			</a>
		</div>

		<div class="nav-menu">
			<sec:authorize access="isAuthenticated()">
				<span class="user-name"><sec:authentication property="principal.member.name"/>様</span>
				<a href="/memberInsert/input">予約一覧</a>
				<a href="/logout" class="btn-secondary">ログアウト</a>
			</sec:authorize>

			<sec:authorize access="isAnonymous()">
				<a href="/memberInsert/input">会員登録</a>
				<a href="/login" class="btn-primary">ログイン</a>
			</sec:authorize>
		</div>
	</div>
</body>
</html>