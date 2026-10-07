package ma.fsac.qa.tests.api;

import io.qameta.allure.restassured.AllureRestAssured;
import io.restassured.builder.RequestSpecBuilder;
import io.restassured.http.ContentType;
import io.restassured.specification.RequestSpecification;
import ma.fsac.qa.config.Config;
import io.restassured.response.Response;
import java.util.function.Supplier;
import ma.fsac.qa.utils.RateLimitHandler;

/** Specification de requete commune aux tests API (URL, cle API, JSON, Allure, gestion du 429). */
public abstract class BaseApiTest {

    protected static final long MAX_TIME_MS = Config.getInt("api.max.response.time");

    protected static RequestSpecification spec() {
        return new RequestSpecBuilder()
                .setBaseUri(Config.apiBaseUrl())
                .setContentType(ContentType.JSON)
                .setAccept(ContentType.JSON)
                // La cle est lue une seule fois (variable REQRES_API_KEY ou config.properties)
                .addHeader("x-api-key", Config.apiKey())
                .addFilter(new AllureRestAssured())
                .build();
    }

    /** Envoie la requete en rejouant automatiquement apres un HTTP 429. */
    protected static Response send(Supplier<Response> call) {
        return RateLimitHandler.send(call);
    }

    protected static String schema(String name) {
        return "schemas/" + name + ".schema.json";
    }
}
