package ma.fsac.qa.pages;

import io.qameta.allure.Step;
import ma.fsac.qa.config.Config;
import org.openqa.selenium.Alert;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;

/** Gestion des alertes JavaScript et des nouveaux onglets. */
public class SwitchWindowPage extends BasePage {

    private static final By NEW_TAB = By.id("new-tab-button");
    private static final By ALERT = By.id("alert-button");

    public SwitchWindowPage(WebDriver driver) {
        super(driver);
    }

    @Step("Ouvrir la page Switch Window")
    public SwitchWindowPage open() {
        open(Config.uiBaseUrl() + "/switch-window");
        visible(NEW_TAB);
        return this;
    }

    @Step("Declencher l'alerte JavaScript")
    public Alert triggerAlert() {
        click(ALERT);
        return waitForAlert();
    }

    @Step("Ouvrir un nouvel onglet et basculer dessus")
    public String openNewTabAndSwitch() {
        String original = driver.getWindowHandle();
        click(NEW_TAB);
        wait.until(ExpectedConditions.numberOfWindowsToBe(2));
        for (String handle : driver.getWindowHandles()) {
            if (!handle.equals(original)) {
                driver.switchTo().window(handle);
                break;
            }
        }
        return original;
    }

    @Step("Fermer l'onglet courant et revenir a la fenetre d'origine")
    public void closeCurrentAndSwitchBackTo(String handle) {
        driver.close();
        driver.switchTo().window(handle);
    }

    public int windowCount() {
        return driver.getWindowHandles().size();
    }
}
