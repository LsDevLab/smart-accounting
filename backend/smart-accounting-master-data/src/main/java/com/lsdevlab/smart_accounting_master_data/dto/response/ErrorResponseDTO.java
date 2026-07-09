package com.lsdevlab.smart_accounting_master_data.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * Standard error response returned by all error-handling paths in the fuel service.
 * Validation errors populate the {@code errors} map; stack traces are only included
 * when the {@code local} Spring profile is active.
 */
@Data
@NoArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ErrorResponseDTO {

    private int status;

    private String message;

    // Only populated for validation errors — maps field name → error message.
    // null (and omitted from JSON) for non-validation errors.
    private Map<String, String> errors;

    // Only populated when "local" profile is active — full stack trace for debugging.
    // null (and omitted from JSON via @JsonInclude) in production.
    private String stackTrace;

    public ErrorResponseDTO(int status, String message) {
        this.status = status;
        this.message = message;
    }

    public ErrorResponseDTO(int status, String message, Map<String, String> errors) {
        this.status = status;
        this.message = message;
        this.errors = errors;
    }
}
