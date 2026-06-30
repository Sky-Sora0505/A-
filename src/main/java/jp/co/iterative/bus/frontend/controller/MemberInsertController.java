package jp.co.iterative.bus.frontend.controller;

import javax.validation.Valid;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.RequestMapping;

import jp.co.iterative.bus.entity.Member;
import jp.co.iterative.bus.frontend.form.MemberInsertForm;
import jp.co.iterative.bus.mapper.MemberMapper;

@Controller
@RequestMapping("memberInsert")
public class MemberInsertController {

	@Autowired
	private MemberMapper memberMapper;

	@RequestMapping("input")
	public String input(MemberInsertForm memberInsertForm, Model model) {

		return "memberInsert/memberInsertInput";
	}
	@RequestMapping("confirm")
	public String confirm(@Valid MemberInsertForm memberInsertForm, BindingResult bindingResult, Model model) {
		if (bindingResult.hasErrors()) {
			return input(memberInsertForm, model);
		}
		return "memberInsert/memberInsertConfirm";
	}
	@RequestMapping("insert")
	public String insert(MemberInsertForm memberInsertForm) {
		Member member = new Member();
		member.setName(memberInsertForm.getName());
		member.setMailAddress(memberInsertForm.getMailAddress1() + memberInsertForm.getMailAddress2());
		member.setTel(memberInsertForm.getTel1() + memberInsertForm.getTel2() + memberInsertForm.getTel3());
		member.setPassword(memberInsertForm.getPassword());
		member.setLoginId(memberInsertForm.getLoginId());

		memberMapper.insertSelective(member);
		return "memberInsert/memberInsertFinish";
	}
}
