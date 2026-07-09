package com.lsdevlab.smart_accounting_master_data.repository;

import com.lsdevlab.smart_accounting_master_data.model.Customer;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface CustomerRepository extends JpaRepository<Customer, UUID> {

}
