#include <iostream>
#include <string>
#include <map>
#include <cmath>

// Базові ціни для різних типів послуг
std::map<std::string, float> base_prices = {
    {"website", 2000.0f},
    {"notes", 100.0f},
    {"programming", 150.0f},
    {"coursework", 500.0f},
    {"other", 200.0f}
};

// Функція для розрахунку ціни на основі типу послуги та довжини опису
extern "C" {
    float calculate_price(const char* service_type, int description_length) {
        std::string service(service_type);
        
        // Отримуємо базову ціну
        float base_price = 200.0f; // дефолтна ціна
        if (base_prices.find(service) != base_prices.end()) {
            base_price = base_prices[service];
        }
        
        // Розраховуємо множник складності на основі довжини опису
        float complexity_multiplier = 1.0f + (description_length / 1000.0f) * 0.5f;
        
        // Обчислюємо фінальну ціну
        float final_price = base_price * complexity_multiplier;
        
        return final_price;
    }
    
    // Функція для валідації email (проста перевірка)
    bool validate_email(const char* email) {
        std::string email_str(email);
        bool has_at = email_str.find('@') != std::string::npos;
        bool has_dot = email_str.find('.') != std::string::npos;
        return has_at && has_dot;
    }
    
    // Функція для розрахунку пріоритету замовлення
    int calculate_priority(const char* service_type, int budget) {
        std::string service(service_type);
        int priority = 1;
        
        // Пріоритет на основі типу послуги
        if (service == "website") priority += 3;
        else if (service == "coursework") priority += 2;
        else if (service == "programming") priority += 1;
        
        // Пріоритет на основі бюджету
        if (budget > 2000) priority += 2;
        else if (budget > 1000) priority += 1;
        
        return priority;
    }
    
    // Функція для розрахунку орієнтовного часу виконання (в днях)
    int estimate_days(const char* service_type, int description_length) {
        std::string service(service_type);
        int base_days = 3;
        
        // Базовий час на основі типу послуги
        if (service == "website") base_days = 7;
        else if (service == "coursework") base_days = 5;
        else if (service == "programming") base_days = 2;
        else if (service == "notes") base_days = 1;
        
        // Додатковий час на основі складності (довжини опису)
        int extra_days = description_length / 500;
        
        return base_days + extra_days;
    }
}

// Тестова функція для перевірки роботи бібліотеки
int main() {
    std::cout << "Тестування C++ модуля обробки замовлень\n";
    std::cout << "====================================\n\n";
    
    // Тест 1: Розрахунок ціни
    float price1 = calculate_price("website", 500);
    std::cout << "Ціна для website (500 символів): " << price1 << " грн\n";
    
    float price2 = calculate_price("notes", 200);
    std::cout << "Ціна для notes (200 символів): " << price2 << " грн\n";
    
    // Тест 2: Валідація email
    bool valid1 = validate_email("test@example.com");
    std::cout << "Email test@example.com валідний: " << (valid1 ? "так" : "ні") << "\n";
    
    bool valid2 = validate_email("invalid-email");
    std::cout << "Email invalid-email валідний: " << (valid2 ? "так" : "ні") << "\n";
    
    // Тест 3: Пріоритет
    int priority1 = calculate_priority("website", 3000);
    std::cout << "Пріоритет для website з бюджетом 3000: " << priority1 << "\n";
    
    // Тест 4: Оцінка часу
    int days1 = estimate_days("website", 1000);
    std::cout << "Орієнтовний час для website (1000 символів): " << days1 << " днів\n";
    
    std::cout << "\n====================================\n";
    std::cout << "Тестування завершено успішно!\n";
    
    return 0;
}
