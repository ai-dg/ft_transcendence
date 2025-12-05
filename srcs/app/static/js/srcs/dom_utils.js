import { FIRST, LAST } from "./const.js";
/**
 * Réinitialise un élément HTML en supprimant ses enfants tout en conservant un certain nombre d'éléments.
 *
 * @param {HTMLElement} element - L'élément dont on veut supprimer les enfants.
 * @param {number} [maxToKeep=0] - Nombre d'éléments à conserver (0 par défaut).
 * @param {FIRST | LAST} [keep=FIRST] - Spécifie si les éléments conservés sont les premiers ou les derniers.
 *                                            Toute autre valeur entraînera la suppression complète du contenu.
 */
export function resetElement(element, maxToKeep = 0, keep = FIRST) {
    if (maxToKeep < 0)
        return;
    if (keep === FIRST) {
        while (element.children.length > maxToKeep) {
            element.removeChild(element.lastChild);
        }
    }
    else if (keep === LAST) {
        while (element.children.length > maxToKeep) {
            element.removeChild(element.firstChild);
        }
    }
    else
        element.innerHTML = "";
}
// Fonction pour placer le curseur à la fin d'un élément éditable
export function editElement(element) {
    // Créer une sélection de texte
    const selection = window.getSelection();
    const range = document.createRange();
    // Placer le point d'insertion à la fin du contenu
    range.selectNodeContents(element);
    range.collapse(false); // false = collapse to end
    // Appliquer la sélection
    selection.removeAllRanges();
    selection.addRange(range);
    // Donner le focus à l'élément
    element.focus();
}
