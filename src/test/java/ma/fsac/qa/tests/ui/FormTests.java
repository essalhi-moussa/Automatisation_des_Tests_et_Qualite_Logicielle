package ma.fsac.qa.tests.ui;

import static org.assertj.core.api.Assertions.assertThat;

import io.qameta.allure.Description;
import io.qameta.allure.Epic;
import io.qameta.allure.Feature;
import io.qameta.allure.Severity;
import io.qameta.allure.SeverityLevel;
import ma.fsac.qa.base.BaseTest;
import ma.fsac.qa.pages.FormPage;
import ma.fsac.qa.pages.ThanksPage;
import ma.fsac.qa.utils.TestData;
import org.testng.annotations.Test;

@Epic("Interface utilisateur")
@Feature("Formulaire d'inscription (/form)")
public class FormTests extends BaseTest {

    @Test(groups = {"smoke", "ui"}, dataProvider = "inscriptionsValides", dataProviderClass = TestData.class,
            description = "UI-01 : inscription valide")
    @Severity(SeverityLevel.CRITICAL)
    @Description("Remplit tous les champs du formulaire puis verifie la page de confirmation.")
    public void inscriptionValide(String prenom, String nom, String poste, int niveau, int sexe,
                                  String experience, String date) {
        FormPage form = new FormPage(getDriver()).open()
                .firstName(prenom).lastName(nom).jobTitle(poste)
                .educationLevel(niveau).sex(sexe).experience(experience).date(date);

        assertThat(form.firstNameValue()).isEqualTo(prenom);
        assertThat(form.isEducationSelected(niveau)).isTrue();
        assertThat(form.isSexChecked(sexe)).isTrue();
        assertThat(form.selectedExperience()).isEqualTo(experience);

        ThanksPage thanks = form.submit();
        assertThat(thanks.currentUrl()).endsWith("/thanks");
        assertThat(thanks.heading()).isEqualTo("Thanks for submitting your form");
        assertThat(thanks.confirmationMessage()).contains("The form was successfully submitted!");
    }

    @Test(groups = "ui", description = "UI-02 : soumission avec champs vides")
    @Severity(SeverityLevel.NORMAL)
    @Description("Formy ne valide pas les champs obligatoires : la soumission d'un formulaire vide aboutit quand meme. "
            + "Le test documente ce comportement reel (constat pour le rapport).")
    public void soumissionFormulaireVide() {
        ThanksPage thanks = new FormPage(getDriver()).open().submit();
        assertThat(thanks.confirmationMessage()).contains("successfully submitted");
    }

    @Test(groups = "ui", dataProvider = "experiences", dataProviderClass = TestData.class,
            description = "UI-03 : liste deroulante des annees d'experience")
    @Severity(SeverityLevel.NORMAL)
    public void listeDeroulanteExperience(String libelle) {
        FormPage form = new FormPage(getDriver()).open().experience(libelle);
        assertThat(form.selectedExperience()).isEqualTo(libelle);
    }
}
