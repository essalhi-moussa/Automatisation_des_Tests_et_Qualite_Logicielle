package ma.fsac.qa.tests.ui;

import static org.assertj.core.api.Assertions.assertThat;

import io.qameta.allure.Epic;
import io.qameta.allure.Feature;
import ma.fsac.qa.base.BaseTest;
import ma.fsac.qa.pages.ModalPage;
import org.testng.annotations.Test;

@Epic("Interface utilisateur")
@Feature("Pop-up modal (/modal)")
public class ModalTests extends BaseTest {

    @Test(groups = {"smoke", "ui"}, description = "UI-04 : ouverture et fermeture du modal (bouton Close)")
    public void ouvrirPuisFermerLeModal() {
        ModalPage page = new ModalPage(getDriver()).open();
        assertThat(page.isModalDisplayed()).isFalse();

        page.openModal();
        assertThat(page.isModalDisplayed()).isTrue();
        assertThat(page.modalTitle()).isEqualTo("Modal title");

        page.close();
        assertThat(page.isModalDisplayed()).isFalse();
    }

    @Test(groups = "ui", description = "UI-05 : le bouton OK du modal ne ferme pas le pop-up")
    public void boutonOkSansEffetDeFermeture() {
        // Comportement reel constate sur Formy : OK n'a pas data-dismiss, seul Close ferme le modal.
        ModalPage page = new ModalPage(getDriver()).open().openModal();
        page.ok();
        assertThat(page.isModalDisplayed()).isTrue();
        page.close();
        assertThat(page.isModalDisplayed()).isFalse();
    }
}
