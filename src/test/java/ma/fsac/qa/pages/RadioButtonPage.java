package ma.fsac.qa.pages;

import io.qameta.allure.Step;
import ma.fsac.qa.config.Config;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

/** Sur /radiobutton seul le premier bouton possede un id : on cible donc par name + value. */
public class RadioButtonPage extends BasePage {

    public RadioButtonPage(WebDriver driver) {
        super(driver);
    }

    private By radio(int index) {
        return By.cssSelector("input[name='exampleRadios'][value='option" + index + "']");
    }

    @Step("Ouvrir la page Radio Button")
    public RadioButtonPage open() {
        open(Config.uiBaseUrl() + "/radiobutton");
        visible(radio(1));
        return this;
    }

    @Step("Selectionner l'option {index}")
    public RadioButtonPage select(int index) {
        click(radio(index));
        return this;
    }

    public boolean isSelected(int index) {
        return visible(radio(index)).isSelected();
    }
}
