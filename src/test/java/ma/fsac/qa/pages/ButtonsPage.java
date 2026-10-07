package ma.fsac.qa.pages;

import io.qameta.allure.Step;
import java.util.List;
import ma.fsac.qa.config.Config;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;

public class ButtonsPage extends BasePage {

    private static final By GROUP_DROPDOWN = By.id("btnGroupDrop1");

    public ButtonsPage(WebDriver driver) {
        super(driver);
    }

    @Step("Ouvrir la page Buttons")
    public ButtonsPage open() {
        open(Config.uiBaseUrl() + "/buttons");
        visible(By.cssSelector("button.btn-success"));
        return this;
    }

    public List<WebElement> allButtons() {
        return driver.findElements(By.cssSelector("button.btn-lg"));
    }

    public boolean allButtonsEnabled() {
        return allButtons().stream().allMatch(WebElement::isEnabled);
    }

    @Step("Cliquer sur le bouton de couleur : {cssClass}")
    public void clickColored(String cssClass) {
        click(By.cssSelector("button." + cssClass));
    }

    @Step("Deplier le groupe de boutons avec menu")
    public List<WebElement> expandGroupDropdown() {
        click(GROUP_DROPDOWN);
        wait.until(d -> d.findElement(By.cssSelector("[aria-labelledby='btnGroupDrop1']")).isDisplayed());
        return driver.findElements(By.cssSelector("[aria-labelledby='btnGroupDrop1'] .dropdown-item"));
    }
}
