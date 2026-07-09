package com.lsdevlab.smart_accounting_master_data;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

@SpringBootApplication
@EnableJpaAuditing
public class SmartAccountingMasterDataApplication {

	public static void main(String[] args) {
		SpringApplication.run(SmartAccountingMasterDataApplication.class, args);
	}

}
