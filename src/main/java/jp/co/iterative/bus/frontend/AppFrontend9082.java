package jp.co.iterative.bus.frontend;

import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;

@SpringBootApplication
@EnableAutoConfiguration
@ComponentScan
@MapperScan("jp.co.iterative.bus.mapper")
public class AppFrontend9082 {
	public static void main(String[] args) {
		SpringApplication.run(AppFrontend9082.class, args);
	}

	/**
	 * Windows環境（Eclipse）でも確実に動作するアクセスログフィルター。
	 * ファイルを作成せずコンソール（標準出力）に直接ログを流します。
	 * URLの後ろのクエリ文字列（?以降）は表示しますが、POSTパラメータ等の内部値は表示しません。
	 */
	@Bean
	public Filter accessLogFilter() {
		return new Filter() {
			private final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MMM/yyyy:HH:mm:ss +0900");

			@Override
			public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
					throws IOException, ServletException {

				// 1. 先に本来の処理（コントローラーの実行やSQLクエリなど）を完了させる
				chain.doFilter(request, response);

				// 2. 処理が終わった後、レスポンスの状況をコンソールへ出力
				if (request instanceof HttpServletRequest && response instanceof HttpServletResponse) {
					HttpServletRequest req = (HttpServletRequest) request;
					HttpServletResponse res = (HttpServletResponse) response;

					String ip = req.getRemoteAddr();
					String time = LocalDateTime.now().format(formatter);
					String method = req.getMethod();
					String uri = req.getRequestURI();
					String protocol = req.getProtocol();
					int status = res.getStatus();

					// URLの「?」以降のクエリ文字列を取得
					String queryString = req.getQueryString();

					// クエリ文字列が存在する場合は「URI?クエリ文字列」、存在しない場合は「URI」のみにする
					String fullPath = (queryString != null) ? uri + "?" + queryString : uri;

					// Qiitaの記事に準拠した標準的なフォーマットでコンソールに出力
					System.out.println(String.format("%s - - [%s] \"%s %s %s\" %d -", ip, time, method, fullPath, protocol, status));
				}
			}
		};
	}
}
