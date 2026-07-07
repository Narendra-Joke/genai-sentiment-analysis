package com.root.repository;

import com.root.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface ProductRepository extends JpaRepository<Product, Integer> {
    @Query("SELECT p FROM Product p WHERE YEAR(p.releasedDate) = :year")
    List<Product> findByReleaseYear(@Param("year") int year);
}