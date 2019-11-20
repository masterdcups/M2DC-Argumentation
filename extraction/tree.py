from lxml import etree

"""
HTML structure of a wikidebat page:

line 393: La prohibition est inefficace

<h2><span id="Arguments_POUR"></span></h2>

### FIRST H3 (class of arguments) is outside <div class="titre-argument">
<h3>
    <span id="1._La_prohibition_est_inefficace">
        1. La prohibition est inefficace
    </span>
</h3>
<div class="titre-argument">
    <h4 class="fr-collapsible-toggle-collapsed-argupour">
        <span id="La consommation_de_cannabis_augmente">
            La consommation de cannabis augmente
        </span>
    </h4>

    <div class="contenu-argument">
    </div>

    <div align="left">
        <div class="NavFramex">
            <div class="NavHead">
                Objections
            </div>
            <div class="NavContent">
                <div class="titre-objection">
                    <h5 class="fr-collapsible-toggle-collapsed-objection">
                        <span id="Il_y_a_des_signes_de_fléchissement_de_la_consommation"></span>
                        <span class="mw-headline" id="Il_y_a_des_signes_de_fl.C3.A9chissement_de_la_consommation">
                            Il y a des signes de fléchissement de la consommation
                        </span>
                    </h5>
                    <div class="contenu-objection">
                        <div class="citation"></div>
                        <div class="reference-citation"></div>

                        <div class="bandeau-section bandeau-niveau-detail loupe noprint">
                            Objection détaillée&#160;: 
                        </div>

                        <div class="bandeau-section bandeau-niveau-detail loupe noprint">
                            Débat connexe&#160;:
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>


    <div class="contenu-argument"></div>

    <h3>
        <span id="2._La_prohibition_est_préjudiciable_aux_usagers">
            2. La prohibition est préjudiciable aux usagers
        </span>
        etc...
    </h3>
</div>

"""

def main():
    tree = etree.parse('debat_pretty.html') 

    for element in tree.xpath(
            './/h2[span[@id="Arguments_POUR"]] \
            /following-sibling::div[contains(@class, "titre-argument")] \
            /h3 \
            /span[contains(@class, "mw-headline")]'
    ):
        print(element.tag, element.text)

if __name__ == '__main__':
    main()
