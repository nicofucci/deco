export const formatCurrency = (value: number) =>
    new Intl.NumberFormat("es-ES", {
        style: "currency",
        currency: "EUR",
        minimumFractionDigits: 2,
    }).format(value);
