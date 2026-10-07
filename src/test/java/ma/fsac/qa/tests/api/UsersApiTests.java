package ma.fsac.qa.tests.api;

import static io.restassured.RestAssured.given;
import static io.restassured.module.jsv.JsonSchemaValidator.matchesJsonSchemaInClasspath;
import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.lessThan;
import static org.hamcrest.Matchers.notNullValue;

import io.qameta.allure.Description;
import io.qameta.allure.Epic;
import io.qameta.allure.Feature;
import io.qameta.allure.Severity;
import io.qameta.allure.SeverityLevel;
import io.restassured.response.Response;
import java.util.Map;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

@Epic("API Reqres")
@Feature("Utilisateurs")
public class UsersApiTests extends BaseApiTest {

    @DataProvider(name = "nouveauxUtilisateurs")
    public Object[][] nouveauxUtilisateurs() {
        return new Object[][] {
            {"morpheus", "leader"},
            {"Yassine Essalhi", "Ingenieur QA"},
        };
    }

    @Test(groups = {"smoke", "api"}, description = "API-01 : GET /api/users?page=2")
    @Severity(SeverityLevel.CRITICAL)
    @Description("Liste paginee : statut 200, pagination coherente, schema JSON, temps de reponse.")
    public void listerLesUtilisateurs() {
        Response r = send(() -> given().spec(spec()).queryParam("page", 2).when().get("/api/users"));
        r.then()
                .statusCode(200)
                .time(lessThan(MAX_TIME_MS))
                .body("page", equalTo(2))
                .body("per_page", equalTo(6))
                .body("data", hasSize(6))
                .body("data[0].id", equalTo(7))
                .body("data.email", everyItem(containsString("@")))
                .body(matchesJsonSchemaInClasspath(schema("users-list")));
    }

    @Test(groups = "api", description = "API-02 : GET /api/users/2")
    public void consulterUnUtilisateur() {
        Response r = send(() -> given().spec(spec()).when().get("/api/users/2"));
        r.then()
                .statusCode(200)
                .time(lessThan(MAX_TIME_MS))
                .body("data.id", equalTo(2))
                .body("data.first_name", equalTo("Janet"))
                .body("data.last_name", equalTo("Weaver"))
                .body(matchesJsonSchemaInClasspath(schema("user-single")));
    }

    @Test(groups = "api", description = "API-03 : GET /api/users/23 (utilisateur inexistant)")
    @Description("Cas negatif : l'API renvoie 404 avec un objet JSON vide.")
    public void utilisateurInexistant() {
        Response r = send(() -> given().spec(spec()).when().get("/api/users/23"));
        assertThat(r.statusCode()).isEqualTo(404);
        assertThat(r.jsonPath().getMap("$")).doesNotContainKey("data");
        assertThat(r.time()).isLessThan(MAX_TIME_MS);
    }

    @Test(groups = {"smoke", "api"}, dataProvider = "nouveauxUtilisateurs",
            description = "API-04 : POST /api/users")
    @Description("Creation : 201, les donnees envoyees sont renvoyees, id et createdAt generes. "
            + "L'enregistrement n'est pas persiste par Reqres.")
    public void creerUnUtilisateur(String name, String job) {
        Response r = send(() -> given().spec(spec()).body(Map.of("name", name, "job", job))
                .when().post("/api/users"));
        r.then()
                .statusCode(201)
                .time(lessThan(MAX_TIME_MS))
                .body("name", equalTo(name))
                .body("job", equalTo(job))
                .body("id", notNullValue())
                .body("createdAt", notNullValue())
                .body(matchesJsonSchemaInClasspath(schema("user-created")));
    }

    @Test(groups = "api", description = "API-05 : PUT /api/users/2")
    public void modifierUnUtilisateur() {
        Response r = send(() -> given().spec(spec()).body(Map.of("name", "morpheus", "job", "zion resident"))
                .when().put("/api/users/2"));
        r.then()
                .statusCode(200)
                .time(lessThan(MAX_TIME_MS))
                .body("name", equalTo("morpheus"))
                .body("job", equalTo("zion resident"))
                .body("updatedAt", notNullValue())
                .body(matchesJsonSchemaInClasspath(schema("user-updated")));
    }

    @Test(groups = "api", description = "API-06 : DELETE /api/users/2")
    public void supprimerUnUtilisateur() {
        Response r = send(() -> given().spec(spec()).when().delete("/api/users/2"));
        assertThat(r.statusCode()).isEqualTo(204);
        assertThat(r.asString()).isEmpty();
        assertThat(r.time()).isLessThan(MAX_TIME_MS);
    }

    @Test(groups = "api", description = "API-07 : POST /api/login valide")
    public void connexionValide() {
        Response r = send(() -> given().spec(spec())
                .body(Map.of("email", "eve.holt@reqres.in", "password", "cityslicka"))
                .when().post("/api/login"));
        r.then()
                .statusCode(200)
                .body("token", notNullValue())
                .body(matchesJsonSchemaInClasspath(schema("login-success")));
    }

    @Test(groups = "api", description = "API-08 : POST /api/login sans mot de passe")
    @Description("Cas negatif : 400 avec le message 'Missing password'.")
    public void connexionSansMotDePasse() {
        Response r = send(() -> given().spec(spec()).body(Map.of("email", "peter@klaven"))
                .when().post("/api/login"));
        r.then()
                .statusCode(400)
                .body("error", equalTo("Missing password"))
                .body(matchesJsonSchemaInClasspath(schema("error")));
    }
}
