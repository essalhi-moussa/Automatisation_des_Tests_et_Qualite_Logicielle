package ma.fsac.qa.pages;

import io.qameta.allure.Step;
import ma.fsac.qa.config.Config;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

public class CheckboxPage extends BasePage {

    public CheckboxPage(WebDriver driver) {
        super(driver);
    }

    @Step("Ouvrir la page Checkbox")
    public CheckboxPage open() {
        open(Config.uiBaseUrl() + "/checkbox");
        visible(By.id("checkbox-1"));
        return this;
    }

    @Step("Basculer la case n°{index}")
    public CheckboxPage toggle(int index) {
        click(By.id("checkbox-" + index));
        return this;
    }

    public boolean isChecked(int index) {
        return visible(By.id("checkbox-" + index)).isSelected();
    }
}
