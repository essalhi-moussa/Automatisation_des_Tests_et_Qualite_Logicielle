package ma.fsac.qa.pages;

import io.qameta.allure.Step;
import ma.fsac.qa.config.Config;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

/** Elements actives / desactives. */
public class EnabledPage extends BasePage {

    public EnabledPage(WebDriver driver) {
        super(driver);
    }

    @Step("Ouvrir la page Enabled and disabled elements")
    public EnabledPage open() {
        open(Config.uiBaseUrl() + "/enabled");
        visible(By.id("input"));
        return this;
    }

    public boolean isDisabledInputEnabled() {
        return visible(By.id("disabledInput")).isEnabled();
    }

    public boolean isActiveInputEnabled() {
        return visible(By.id("input")).isEnabled();
    }

    @Step("Saisir dans le champ actif : {value}")
    public String typeInActiveInput(String value) {
        type(By.id("input"), value);
        return visible(By.id("input")).getAttribute("value");
    }
}
