// LICENSE GPL 3.0 Peter Pilgrim, Xenonique.co.uk, 2012
// http://www.gnu.org/licenses/gpl.html GNU PUBLIC LICENSE 3.0

/**
 * Implementation type com.comp6239.HttpStatusCode
 * <p>
 * (Only codes 400 to 417 and codes 500 to 524 implemented)
 *
 * @see "http://en.wikipedia.org/wiki/List_of_HTTP_status_codes"
 */

package com.comp6239;

public enum HttpStatusCode {
    CONTINUE(100, "Continue"),
    SWITCHING_PROTOCOL(101, "Switching Protocols"),
    PROCESSING(102, "Processing"),

    OK(200, "OK"),
    CREATED(201, "Created"),
    ACCEPTED(202, "Accepted"),
    NON_AUTHORITATIVE_INFORMATION(203, "Non-Authoritative Information"),
    NO_CONTENT(204, "No Content"),
    RESET_CONTENT(205, "Reset Content"),
    PARTIAL_CONTENT(206, "Partial Content"),
    MULTI_STATUS(207, "Multi-Status"),
    ALREADY_REPORTED(208, "Already Reported"),
    IM_USED(226, "IM Used (RFC 3229)"),

    MULTIPLE_CHOICES(300, "Multiple Choices"),
    MOVED_PERMANENTLY(301, "Moved Permanently"),
    FOUND(302, "Found"),
    SEE_OTHER(303, "See Other"),
    NOT_MODIFIED(304, "Not Modified"),
    USE_PROXY(305, "Use Proxy"),
    SWITCH_PROXY(306, "Switch Proxy"),
    TEMPORARY_REDIRECT(307, "Temporary Redirect"),
    PERMANENT_REDIRECT(308, "Permanent Redirect"),

    BAD_REQUEST(400, "Bad Request"),
    UNAUTHORIZED(401, "Unauthorized"),
    PAYMENT_REQUIRED(402, "Payment Required"),
    FORBIDDEN(403, "Forbidden"),
    NOT_FOUND(404, "Not Found"),
    METHOD_NOT_ALLOWED(405, "Method Not Allowed"),
    NOT_ACCEPTABLE(406, "Not Acceptable"),
    PROXY_AUTHENTICATION_REQUIRED(407, "Proxy Authentication Required"),
    REQUEST_TIMEOUT(408, "Request Timeout"),
    CONFLICT(409, "Conflict"),
    GONE(410, "Gone"),
    LENGTH_REQUIRED(411, "Length Required"),
    PRECONDITION_FAILED(412, "Precondition Failed"),
    REQUEST_ENTITY_TOO_LARGE(413, "Request Entity Too Large"),
    REQUEST_URI_TOO_LONG(414, "Request-URI Too Long"),
    UNSUPPORTED_MEDIA_TYPE(415, "Unsupported Media Type"),
    REQUESTED_RANGE_NOT_SATISFIABLE(416, "Requested Range Not Satisfiable"),
    EXPECTATION_FAILED(417, "Expectation Failed"),
    TEAPOT(418, "I'm a teapot"),
    MISDIRECTED_REQUEST(421, "Misdirected Request"),
    UNPROCESSABLE_ENTITY(422, "Unprocessable Entity"),
    LOCKED(423, "Locked"),
    FAILED_DEPENDENCY(424, "Failed Dependency"),
    UPGRADE_REQUIRED(426, "Upgrade Required"),
    PRECONDITION_REQURED(427, "Precondition Required"),
    TOO_MANY_REQUESTS(428, "Too Many Requests"),
    REQUEST_HEADER_FIELDS_TOO_LARGE(431, "Request Header Fields Too Large"),
    CONNECTION_CLOSED_WITHOUT_RESPONSE(444, "Connection Closed Without Response"),
    UNAVAILABLE_FOR_LEGAL_REASONS(451, "Unavailable For Legal Reasons"),
    CLIENT_CLOSED_REQUEST(499, "Client Closed Request"),

    INTERNAL_SERVER_ERROR(500, "Internal Server Error"),
    NOT_IMPLEMENTED(501, "Not Implemented"),
    BAD_GATEWAY(502, "Bad Gateway"),
    SERVICE_UNAVAILABLE(503, "Service Unavailable"),
    GATEWAY_TIMEOUT(504, "Gateway Timeout"),
    HTTP_VERSION_NOT_SUPPORTED(505, "HTTP Version Not Supported"),
    VARIANT_ALSO_NEGOTIATES(506, "Variant Also Negotiates"),
    INSUFFICIENT_STORAGE(507, "Insufficient Storage"),
    LOOP_DETECTED(508, "Loop Detected"),
    BANDWIDTH_LIMIT_EXCEEDED(509, "Bandwidth Limit Exceeded"),
    NOT_EXTEND(510, "Not Extended"),
    NETWORK_AUTHENTICATION_REQUIRED(511, "Network Authentication Required"),
    CONNECTION_TIMED_OUT(522, "Connection timed out"),
    PROXY_DECLINED_REQUEST(523, "Proxy Declined Request"),
    TIMEOUT_OCCURRED(524, "A timeout occurred"),
    NETWORK_CONNECT_TIMEOUT(599, "Network Connect Timeout Error");

    private int code;
    private String desc;
    private String text;

    HttpStatusCode(int code, String desc) {
        this.code = code;
        this.desc = desc;
        this.text = Integer.toString(code);
    }

    /**
     * Gets the HTTP status code
     * @return the status code number
     */
    public int getCode() {
        return code;
    }

    /**
     * Gets the HTTP status code as a text string
     * @return the status code as a text string
     */
    public String asText() {
        return text;
    }

    /**
     * Get the description
     * @return the description of the status code
     */
    public String getDesc() {
        return desc;
    }

}