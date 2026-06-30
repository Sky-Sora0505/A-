package jp.co.iterative.bus.frontend.form;

import javax.validation.constraints.AssertTrue;
import javax.validation.constraints.NotBlank;

public class MemberInsertForm {
	@NotBlank(message = "氏名を入力してください。")
	private String name;
	@NotBlank(message = "メールアドレスを入力してください。")
	private String mailAddress1;
	private String mailAddress2;
	private String tel1;
	private String tel2;
	private String tel3;
	@NotBlank(message = "パスワードを入力してください。")
	private String password;
	@NotBlank(message = "会員IDを入力してください。")
	private String loginId;
public String getTel1() {
		return tel1;
	}
	public void setTel1(String tel1) {
		this.tel1 = tel1;
	}
	public String getTel2() {
		return tel2;
	}
	public void setTel2(String tel2) {
		this.tel2 = tel2;
	}
	public String getTel3() {
		return tel3;
	}
	public void setTel3(String tel3) {
		this.tel3 = tel3;
	}
	//難波作成多分違う
	@AssertTrue(message = "{error.telNotExist}")
	public Boolean getTel() {
	    if (tel1 == null || tel1.isEmpty() ||
	        tel2 == null || tel2.isEmpty() ||
	        tel3 == null || tel3.isEmpty()) {
	        return false;
	        // falseのときエラーメッセージが出る
	    }
	    return true;
	}
//難波作成多分違う
	@AssertTrue(message = "{error.mailAddressNotExist}")
	public Boolean getMailAddress() {
	    if (mailAddress1 == null || mailAddress1.isEmpty() ||
	        mailAddress2 == null || mailAddress2.isEmpty()) {
	        return false;
	    }
	    return true;
	}

	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getMailAddress1() {
		return mailAddress1;
	}
	public void setMailAddress1(String mailAddress1) {
		this.mailAddress1 = mailAddress1;
	}
	public String getMailAddress2() {
		return mailAddress2;
	}
	public void setMailAddress2(String mailAddress2) {
		this.mailAddress2 = mailAddress2;
	}

	public String getPassword() {
		return password;
	}
	public void setPassword(String password) {
		this.password = password;
	}
	public String getLoginId() {
		return loginId;
	}
	public void setLoginId(String loginId) {
		this.loginId = loginId;
	}

}