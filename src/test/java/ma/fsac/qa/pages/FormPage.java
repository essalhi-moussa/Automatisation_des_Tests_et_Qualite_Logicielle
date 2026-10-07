package ma.fsac.qa.pages;

import io.qameta.allure.Step;
import ma.fsac.qa.config.Config;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;

/** Page /form de Formy, utilisee comme scenario d'inscription (Formy n'a pas de page de login). */
public class FormPage extends BasePage {

    private static final By FIRST_NAME = By.id("first-name");
    private static final By LAST_NAME = By.id("last-name");
    private static final By JOB_TITLE = By.id("job-title");
    private static final By EXPERIENCE = By.id("select-menu");
    private static final By DATE = By.id("datepicker");
    private static final By SUBMIT = By.cssSelector("a.btn.btn-lg.btn-primary[href='/thanks']");

    public FormPage(WebDriver driver) {
        super(driver);
    }

    @Step("Ouvrir le formulaire d'inscription")
    public FormPage open() {
        open(Config.uiBaseUrl() + "/form");
        visible(FIRST_NAME);
        return this;
    }

    @Step("Saisir le prenom : {value}")
    public FormPage firstName(String value) {
        type(FIRST_NAME, value);
        return this;
    }

    @Step("Saisir le nom : {value}")
    public FormPage lastName(String value) {
        type(LAST_NAME, value);
        return this;
    }

    @Step("Saisir le poste : {value}")
    public FormPage jobTitle(String value) {
        type(JOB_TITLE, value);
        return this;
    }

    @Step("Choisir le niveau d'etudes n°{index}")
    public FormPage educationLevel(int index) {
        click(By.id("radio-button-" + index));
        return this;
    }

    @Step("Cocher le sexe n°{index}")
    public FormPage sex(int index) {
        click(By.id("checkbox-" + index));
        return this;
    }

    @Step("Choisir les annees d'experience : {label}")
    public FormPage experience(String label) {
        new Select(visible(EXPERIENCE)).selectByVisibleText(label);
        return this;
    }

    @Step("Saisir la date : {value}")
    public FormPage date(String value) {
        type(DATE, value);
        // le calendrier reste ouvert : on le ferme pour qu'il ne masque pas le bouton
        visible(By.tagName("h1")).click();
        return this;
    }

    @Step("Soumettre le formulaire")
    public ThanksPage submit() {
        WebElement btn = visible(SUBMIT);
        scrollIntoView(btn);
        click(SUBMIT);
        wait.until(ExpectedConditions.textToBePresentInElementLocated(By.tagName("h1"), "Thanks"));
        return new ThanksPage(driver);
    }

    public String selectedExperience() {
        return new Select(visible(EXPERIENCE)).getFirstSelectedOption().getText();
    }

    public boolean isEducationSelected(int index) {
        return visible(By.id("radio-button-" + index)).isSelected();
    }

    public boolean isSexChecked(int index) {
        return visible(By.id("checkbox-" + index)).isSelected();
    }

    public String firstNameValue() {
        return visible(FIRST_NAME).getAttribute("value");
    }
}
