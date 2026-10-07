package ma.fsac.qa.tests.ui;

import static org.assertj.core.api.Assertions.assertThat;

import io.qameta.allure.Epic;
import io.qameta.allure.Feature;
import ma.fsac.qa.base.BaseTest;
import ma.fsac.qa.pages.ButtonsPage;
import ma.fsac.qa.pages.CheckboxPage;
import ma.fsac.qa.pages.DropdownPage;
import ma.fsac.qa.pages.EnabledPage;
import ma.fsac.qa.pages.RadioButtonPage;
import ma.fsac.qa.utils.TestData;
import org.testng.annotations.Test;

@Epic("Interface utilisateur")
@Feature("Composants : dropdown, radio, cases, boutons")
public class ElementsTests extends BaseTest {

    @Test(groups = "ui", dataProvider = "entreesMenu", dataProviderClass = TestData.class,
            description = "UI-08 : navigation via le menu deroulant")
    public void menuDeroulantNavigation(String libelle, String fragmentUrl) {
        DropdownPage page = new DropdownPage(getDriver()).open().expand();
        assertThat(page.itemCount()).isGreaterThanOrEqualTo(10);
        page.choose(libelle);
        assertThat(page.waitForUrlContaining(fragmentUrl)).isTrue();
    }

    @Test(groups = {"smoke", "ui"}, description = "UI-09 : boutons radio mutuellement exclusifs")
    public void boutonsRadioExclusifs() {
        RadioButtonPage page = new RadioButtonPage(getDriver()).open();
        assertThat(page.isSelected(1)).isTrue();

        page.select(3);
        assertThat(page.isSelected(3)).isTrue();
        assertThat(page.isSelected(1)).isFalse();
        assertThat(page.isSelected(2)).isFalse();
    }

    @Test(groups = "ui", description = "UI-10 : cases a cocher independantes")
    public void casesACocher() {
        CheckboxPage page = new CheckboxPage(getDriver()).open();
        assertThat(page.isChecked(1)).isFalse();

        page.toggle(1).toggle(3);
        assertThat(page.isChecked(1)).isTrue();
        assertThat(page.isChecked(2)).isFalse();
        assertThat(page.isChecked(3)).isTrue();

        page.toggle(1);
        assertThat(page.isChecked(1)).isFalse();
    }

    @Test(groups = "ui", description = "UI-11 : boutons actifs et groupe de boutons avec menu")
    public void boutons() {
        ButtonsPage page = new ButtonsPage(getDriver()).open();
        assertThat(page.allButtons()).hasSizeGreaterThanOrEqualTo(6);
        assertThat(page.allButtonsEnabled()).isTrue();

        page.clickColored("btn-success");
        assertThat(page.expandGroupDropdown()).hasSize(2);
    }

    @Test(groups = "ui", description = "UI-12 : champ actif et champ desactive")
    public void champsActifEtDesactive() {
        EnabledPage page = new EnabledPage(getDriver()).open();
        assertThat(page.isDisabledInputEnabled()).isFalse();
        assertThat(page.isActiveInputEnabled()).isTrue();
        assertThat(page.typeInActiveInput("texte de test")).isEqualTo("texte de test");
    }
}
