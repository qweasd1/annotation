import re
import spacy
from app import db
from models import Sense
from spacy.lang.en.stop_words import STOP_WORDS

nlp = spacy.load("en",disable=['parser', 'tagger'])

ABBR_PATTERN = re.compile(r"[A-Z\-_0-9#]+")

abbr_patterns = [
    ABBR_PATTERN
]



sense_inventory = None

def init_abbr_detect():
    global sense_inventory
    if sense_inventory:
        return
    sense_inventory = set([x[0] for x in db.session.query(Sense.abbr).distinct(Sense.abbr).all()])


black_list = set(
    [
        "-"
    ]
)

black_pattern_list = [
    re.compile(r"[0-9a-z]+"),
    re.compile(r"[A-Z][a-z]*")
]


def some(array, fn):
    for item in array:
        if fn(item):
            return True
    return False


def detect_abbr(text):
    init_abbr_detect()
    tokens = nlp(text)
    result = []

    for token in tokens:
        if token.text not in black_list and not some(black_pattern_list,lambda p:p.fullmatch(token.text)) and (token.lemma_ not in STOP_WORDS and token.text in sense_inventory and token.text or some(
                abbr_patterns, lambda p: p.fullmatch(token.text))):
            result.append("|{0}|".format(token.text) + " ")
        else:
            result.append(token.text + " ")
    return "".join(result)

def genereate_annotation_text_json(text):
    init_abbr_detect()
    tokens = nlp(text)
    result = []
    for token in tokens:
        if token.text not in black_list and not some(black_pattern_list,lambda p:p.fullmatch(token.text)) and (token.lemma_ not in STOP_WORDS and token.text in sense_inventory and token.text or some(
                abbr_patterns, lambda p: p.fullmatch(token.text))):
            result.append({
                "text":token.text,
                "type":"like"
            })
        else:
            result.append({
                "text":token.text,
                "type":"normal"
            })
    return result

def get_sense_inventory():
    global sense_inventory
    init_abbr_detect()
    return sense_inventory


# text = "In recent years, several synthetic strategies aiming at the peripheral functionalization of porphyrins were developed. Particularly interesting are those involving the modification of β-pyrrolic positions leading to pyrrole-modified porphyrins containing four-, five-, six- or seven-membered heterocycles. Azeteoporphyrins, porpholactones and morpholinoporphyrins are representative examples of such porphyrinoids. These porphyrin derivatives have recently gained an increasing interest due to their potential application in PDT, as multimodal imaging contrast agents, NIR-absorbing dyes, optical sensors for oxygen, cyanide, hypochlorite and pH, and in catalysis."
# # text = "A new liquid chromatography-tandem mass spectrometry (LC-MS/MS) method is developed for the quantification of dehydrodiisoeugenol (DDIE) in rat cerebral nuclei after single intravenous administration. DDIE and daidzein (internal standard) were separated on a Diamonsil™ ODS C18 column with methanol-water containing 0.1% formic acid (81:19, v/v) as a mobile phase. Detection of DDIE was performed on a positive electrospray ionization source using a triple quadrupole mass spectrometer. DDIE and daidzein were monitored at m/z 327.2→188.0 and m/z 255.0→199.2, respectively, in multiple reaction monitoring mode. This method enabled quantification of DDIE in various brain areas, including, cortex, hippocampus, striatum, hypothalamus, cerebellum and brainstem, with high specificity, precision, accuracy, and recovery. The data herein demonstrate that our new LC-MS/MS method is highly sensitive and suitable for monitoring cerebral nuclei distribution of DDIE."
# # text = "Remote ischemic perconditioning (PerC) has been proved to have neuroprotective effects on cerebral ischemia, however, the effect of PerC on the BBB disruption and underlying mechanisms remains largely unknown. To address these issues, total 90 adult male Sprague Dawley (SD) rats were used. The rats underwent 90-min middle cerebral artery occlusion (MCAO), and the limb remote ischemic PerC was immediately applied after the onset of MCAO. We found that limb remote PerC protected BBB breakdown and brain edema, in parallel with reduced infarct volume and improved neurological deficits, after MCAO. Immunofluorescence studies revealed that MCAO resulted in disrupted continuity of claudin-5 staining in the cerebral endothelial cells with significant gap formation, which was significantly improved after PerC. Western blot analysis demonstrated that expression of tight junction (TJ) protein occludin was significantly increased, but other elements of TJ proteins, claudin-5 and ZO-1, in the BBB endothelial cells were not altered at 48 h after PerC, compared to MCAO group. The expression of matrix metalloproteinase (MMP-9), which was involved in TJ protein degradation, was decreased after PerC. Interestingly, phosphorylated extracellular signal-regulated kinase 1/2 (pERK1/2), an upstream of MMP-9 signaling, was significantly reduced in the PerC group. Our data suggest that PerC inhibits MMP-9-mediated occludin degradation, which could lead to decreased BBB disruption and brain edema after ischemic stroke."
# # text = "Upon arrival to OSH, his VS= 96.9 154/77 81 226 100%6L. He was speaking in 1 word sentences, with audibly wheezing, and did not tolerate lying flat. He was placed on BiPaP. ABG 7.26/80/103. His labs were notable for NA 114. CXR c/w CHF, ECG showed sinus, no ste/std. He was treated for CHF, and COPD flare with 120mg iv lasix x1 @ 17:35, duonebs, solumedrol 125mg iv x 1. He made 600 cc UOP at 19:15. He was transferred to [**Hospital1 18**] for further management."
# print(genereate_annotation_text_json(text))
# print(get_abbrs(text))
