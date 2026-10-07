package ma.fsac.qa.utils;

import io.restassured.response.Response;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import ma.fsac.qa.config.Config;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Reqres limite le debit (en-tetes Ratelimit-*). Sur HTTP 429, on attend le delai indique par
 * Ratelimit-Reset (borne par api.rate.limit.max.wait) puis on rejoue la requete.
 * Les 429 observes sont comptabilises pour etre reportes dans le rapport.
 */
public final class RateLimitHandler {

    private static final Logger LOG = LoggerFactory.getLogger(RateLimitHandler.class);
    private static final AtomicInteger COUNT_429 = new AtomicInteger();

    private RateLimitHandler() {
    }

    public static int observed429() {
        return COUNT_429.get();
    }

    public static Response send(Supplier<Response> call) {
        int maxRetries = Config.getInt("api.rate.limit.max.retries");
        long maxWait = Config.getInt("api.rate.limit.max.wait");

        Response response = call.get();
        int attempt = 0;
        while (response.statusCode() == 429 && attempt < maxRetries) {
            COUNT_429.incrementAndGet();
            long wait = Math.min(maxWait, parseReset(response));
            LOG.warn("HTTP 429 : attente de {} s avant nouvelle tentative ({}/{})", wait, attempt + 1, maxRetries);
            try {
                Thread.sleep(wait * 1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
            attempt++;
            response = call.get();
        }
        return response;
    }

    private static long parseReset(Response response) {
        String value = response.getHeader("Ratelimit-Reset");
        if (value == null) {
            value = response.getHeader("Retry-After");
        }
        try {
            return value == null ? 20 : Long.parseLong(value.trim()) + 1;
        } catch (NumberFormatException e) {
            return 20;
        }
    }
}
