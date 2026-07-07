package com.root.oauth;

import com.root.entity.User;
import com.root.jwt.JwtService;
import com.root.repository.UserRepository;
import jakarta.servlet.http.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
public class CustomAuthSuccessHandler implements AuthenticationSuccessHandler {

    @Autowired
    private JwtService jwtService;

    @Autowired
    private UserRepository userRepository;

    @Value("${app.frontend.url}")
    private String frontendUrl;

    @Override
    public void onAuthenticationSuccess(
            HttpServletRequest request,
            HttpServletResponse response,
            Authentication authentication
    ) throws IOException {

        String email = authentication.getName();

        User user = userRepository.findByEmail(email).orElseThrow();

        String token = jwtService.generateToken(
                user.getEmail(),
                user.getName(),
                user.getImage()
        );

        String redirectUrl = frontendUrl + "/oauth-success?token=" + token;

        response.sendRedirect(redirectUrl);
    }
}