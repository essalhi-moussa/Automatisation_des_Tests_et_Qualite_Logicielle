package ma.fsac.qa.pages;

import io.qameta.allure.Step;
import ma.fsac.qa.config.Config;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;

public class ModalPage extends BasePage {

    private static final By OPEN_BUTTON = By.id("modal-button");
    private static final By MODAL = By.id("exampleModal");
    private static final By CLOSE_BUTTON = By.id("close-button");
    private static final By OK_BUTTON = By.id("ok-button");
    private static final By TITLE = By.id("exampleModalLabel");

    public ModalPage(WebDriver driver) {
        super(driver);
    }

    @Step("Ouvrir la page Modal")
    public ModalPage open() {
        open(Config.uiBaseUrl() + "/modal");
        visible(OPEN_BUTTON);
        return this;
    }

    @Step("Cliquer sur le bouton d'ouverture du pop-up")
    public ModalPage openModal() {
        click(OPEN_BUTTON);
        visible(MODAL);
        return this;
    }

    @Step("Fermer le pop-up avec le bouton Close")
    public ModalPage close() {
        click(CLOSE_BUTTON);
        wait.until(ExpectedConditions.invisibilityOfElementLocated(MODAL));
        return this;
    }

    /** Sur Formy le bouton OK n'a aucun gestionnaire : il ne ferme pas le pop-up. */
    @Step("Cliquer sur le bouton OK du pop-up")
    public ModalPage ok() {
        click(OK_BUTTON);
        return this;
    }

    public boolean isModalDisplayed() {
        return !driver.findElements(MODAL).isEmpty() && driver.findElement(MODAL).isDisplayed();
    }

    public String modalTitle() {
        return textOf(TITLE);
    }
}
