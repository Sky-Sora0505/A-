package jp.co.iterative.bus.frontend.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.RequestMapping;

import jp.co.iterative.bus.frontend.form.LoginForm;

/**
 * ログインコントローラ。
 */
@Controller
public class LoginController {

	/**
	 * モデルアトリビュート。
	 * @return ログインフォーム
	 */
	@ModelAttribute
	public LoginForm createForm() {
		return new LoginForm();
	}

	/**
	 * ログイン画面を表示する。
	 * @param loginForm ログインフォーム
	 * @return ログイン画面
	 */
	@RequestMapping("/login")
	public String login(LoginForm loginForm) {

		return "login";
	}
}
