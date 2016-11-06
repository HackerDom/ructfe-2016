package cartographer

import org.springframework.boot.CommandLineRunner
import org.springframework.boot.SpringApplication
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.context.annotation.Bean

@SpringBootApplication
open class Application {
    @Bean
    open fun init() = CommandLineRunner {
        System.out.println("Ima running, bitch!")
    }
}

fun main(args: Array<String>) {
    SpringApplication.run(Application::class.java, *args)
}