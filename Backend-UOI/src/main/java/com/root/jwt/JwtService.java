package com.root.jwt;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.Date;

@Service
public class JwtService {

    @Value("${app.jwt.secret}")
    private String secret;

    public String generateToken(String email,String name,String picture){

        return Jwts.builder()
                .setSubject(email)
                .claim("name",name)
                .claim("picture",picture)
                .setIssuedAt(new Date())
//                .setExpiration(new Date(System.currentTimeMillis()+300000))
                .setExpiration(new Date(System.currentTimeMillis() + 60 * 60 * 1000))
                .signWith(
                        Keys.hmacShaKeyFor(secret.getBytes()),
                        SignatureAlgorithm.HS256
                )
                .compact();
    }

}
