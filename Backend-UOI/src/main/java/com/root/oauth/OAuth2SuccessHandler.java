package com.root.oauth;

import com.root.entity.User;
import com.root.jwt.JwtService;
import com.root.repository.UserRepository;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.Optional;

@Component
public class OAuth2SuccessHandler extends SimpleUrlAuthenticationSuccessHandler {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private JwtService jwtService;

    @Value("${app.frontend.url}")
    private String frontendUrl;

    @Override
    public void onAuthenticationSuccess(
            HttpServletRequest request,
            HttpServletResponse response,
            Authentication authentication
    ) throws IOException {

        OAuth2User oauthUser = (OAuth2User) authentication.getPrincipal();

        String email = oauthUser.getAttribute("email");
        String picture = oauthUser.getAttribute("picture");
        System.out.println("Picture : " + picture);
        String name = oauthUser.getAttribute("name");

        Optional<User> userOptional = userRepository.findByEmail(email);

        if(userOptional.isEmpty()){
            response.sendRedirect(frontendUrl + "/login?error=user_not_found");
            return;
        }

        User user = userOptional.get();

//        user.setImage(picture);
//        userRepository.save(user);

        String token = jwtService.generateToken(email,name,picture);

        String redirectUrl = frontendUrl + "/oauth-success?token=" + token;

        getRedirectStrategy().sendRedirect(request,response,redirectUrl);
    }
}
