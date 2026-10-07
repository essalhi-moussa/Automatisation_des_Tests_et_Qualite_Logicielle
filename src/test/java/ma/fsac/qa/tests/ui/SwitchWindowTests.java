package ma.fsac.qa.tests.ui;

import static org.assertj.core.api.Assertions.assertThat;

import io.qameta.allure.Epic;
import io.qameta.allure.Feature;
import ma.fsac.qa.base.BaseTest;
import ma.fsac.qa.config.Config;
import ma.fsac.qa.pages.SwitchWindowPage;
import org.openqa.selenium.Alert;
import org.testng.annotations.Test;

@Epic("Interface utilisateur")
@Feature("Alertes et fenetres (/switch-window)")
public class SwitchWindowTests extends BaseTest {

    @Test(groups = {"smoke", "ui"}, description = "UI-06 : alerte JavaScript acceptee")
    public void alerteJavaScriptAcceptee() {
        SwitchWindowPage page = new SwitchWindowPage(getDriver()).open();
        Alert alert = page.triggerAlert();
        assertThat(alert.getText()).isEqualTo("This is a test alert!");
        alert.accept();
        // apres acceptation, la page reste utilisable : l'URL n'a pas change
        assertThat(page.currentUrl()).endsWith("/switch-window");
    }

    @Test(groups = "ui", description = "UI-07 : ouverture d'un nouvel onglet et retour")
    public void nouvelOnglet() {
        SwitchWindowPage page = new SwitchWindowPage(getDriver()).open();
        String origine = page.openNewTabAndSwitch();

        assertThat(page.windowCount()).isEqualTo(2);
        assertThat(page.currentUrl()).startsWith(Config.uiBaseUrl());

        page.closeCurrentAndSwitchBackTo(origine);
        assertThat(page.windowCount()).isEqualTo(1);
        assertThat(page.currentUrl()).endsWith("/switch-window");
    }
}
