package jp.co.iterative.bus.frontend.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;

import jp.co.iterative.bus.frontend.security.MemberAuthenticationProvider;

@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {
	@Autowired
	private MemberAuthenticationProvider authenticationProvider;

	@Override
	protected void configure(AuthenticationManagerBuilder auth) throws Exception {
		auth.authenticationProvider(authenticationProvider);
	}


	@Override
	protected void configure(HttpSecurity http) throws Exception {
		http.csrf().disable();

//		// TODO 開発用
//		http.authorizeRequests()
//		.anyRequest().permitAll();

//		http.authorizeRequests()
//		.antMatchers("/","/login","/routeSearch/*","css/*","images/*","/memberInsert/*").permitAll()
//		.anyRequest()
//		.authenticated();

		http.formLogin()
		.loginPage("/login")
		.loginProcessingUrl("/auth")
		.defaultSuccessUrl("/routeSearch/index", true)
		;

		http.logout()
		.logoutUrl("/logout")
		.logoutSuccessUrl("/routeSearch/index");

	}

}
