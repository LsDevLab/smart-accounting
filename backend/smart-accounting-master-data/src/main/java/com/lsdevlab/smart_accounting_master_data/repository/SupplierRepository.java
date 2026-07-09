package com.lsdevlab.smart_accounting_master_data.repository;

import com.lsdevlab.smart_accounting_master_data.model.Supplier;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

interface SupplierRepository extends JpaRepository<Supplier, UUID> {

}
