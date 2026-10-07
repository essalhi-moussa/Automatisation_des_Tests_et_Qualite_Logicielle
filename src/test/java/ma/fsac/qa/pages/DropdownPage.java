package ma.fsac.qa.pages;

import io.qameta.allure.Step;
import ma.fsac.qa.config.Config;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;

/** Menu deroulant Bootstrap de la page /dropdown (liste de liens de navigation). */
public class DropdownPage extends BasePage {

    private static final By TOGGLE = By.id("dropdownMenuButton");
    private static final By MENU = By.cssSelector(".dropdown-menu[aria-labelledby='dropdownMenuButton']");

    public DropdownPage(WebDriver driver) {
        super(driver);
    }

    @Step("Ouvrir la page Dropdown")
    public DropdownPage open() {
        open(Config.uiBaseUrl() + "/dropdown");
        visible(TOGGLE);
        return this;
    }

    @Step("Deplier le menu")
    public DropdownPage expand() {
        click(TOGGLE);
        visible(MENU);
        return this;
    }

    @Step("Choisir l'entree : {label}")
    public void choose(String label) {
        click(By.xpath("//div[@aria-labelledby='dropdownMenuButton']//a[normalize-space()='" + label + "']"));
    }

    public int itemCount() {
        return driver.findElements(By.cssSelector(".dropdown-menu[aria-labelledby='dropdownMenuButton'] .dropdown-item")).size();
    }

    public boolean waitForUrlContaining(String fragment) {
        return wait.until(ExpectedConditions.urlContains(fragment));
    }
}
