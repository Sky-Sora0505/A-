package jp.co.iterative.bus.frontend.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class SampleController {

	@RequestMapping("/sample")
	public String index() {
		return "sample";
	}
}
